import threading
import time
import cv2
import datetime
import logging
import numpy as np
from ultralytics import YOLO
from database.db import get_db

COLOR_RANGES_HSV = {
    "Green": ([40, 50, 50], [80, 255, 255]),
    "Blue": ([100, 50, 50], [130, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255]),
}

RED_RANGES_HSV = (
    ([0, 100, 100], [10, 255, 255]),
    ([160, 100, 100], [180, 255, 255]),
)

MAX_TRACKED_IDS = 500


class VisionSystem:

    def __init__(self, motor_controller):
        self.motor_controller = motor_controller
        self.model = YOLO("best.pt")

        self.counted_ids = set()
        self.running = False
        self._thread = None

        self._frame = None
        self._frame_lock = threading.Lock()

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._update, daemon=True)
        self._thread.start()
        logging.info("VisionSystem started")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)

    def get_frame(self):
        with self._frame_lock:
            return self._frame.copy() if self._frame is not None else None

    # ─────────────────────────────
    # CAMERA LOOP - picamera2
    # ─────────────────────────────
    def _update(self):
        try:
            from picamera2 import Picamera2
        except ImportError:
            logging.error("picamera2 not installed. Run: pip install picamera2 --break-system-packages")
            return

        picam2 = Picamera2()

        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()

        # warmup
        time.sleep(2)

        logging.info("Camera started successfully (picamera2)")

        while self.running:

            frame = picam2.capture_array()

            if frame is None or frame.size == 0:
                logging.warning("Empty frame, retrying...")
                time.sleep(0.1)
                continue

            # YOLO inference
            try:
                result = self.model.track(
                    frame,
                    persist=True,
                    tracker="bytetrack.yaml",
                    verbose=False
                )[0]
            except Exception as e:
                logging.error(f"YOLO error: {e}")
                continue

            # detection parsing
            boxes, ids, classes = [], [], []

            if result.boxes.id is not None:
                ids = result.boxes.id.int().cpu().tolist()
                boxes = result.boxes.xyxy.cpu().tolist()
                classes = result.boxes.cls.int().cpu().tolist()

            for box, obj_id, cls in zip(boxes, ids, classes):

                x1, y1, x2, y2 = map(int, box)
                centerx = (x1 + x2) // 2

                if centerx <= 150 and obj_id not in self.counted_ids:

                    if len(self.counted_ids) >= MAX_TRACKED_IDS:
                        self.counted_ids.clear()

                    self.counted_ids.add(obj_id)

                    color = self._detect_color(frame[y1:y2, x1:x2])
                    self._insert_into_db(self.model.names[cls], color)

                    if cls != 0:
                        self.motor_controller.run_pusher(3)

            annotated = self._annotate(result.plot())

            with self._frame_lock:
                self._frame = annotated

        picam2.stop()
        logging.info("Camera released")

    # ─────────────────────────────
    # COLOR DETECTION
    # ─────────────────────────────
    def _detect_color(self, obj):
        if obj is None or obj.size == 0:
            return "Unknown"

        total = obj.shape[0] * obj.shape[1]
        hsv = cv2.cvtColor(obj, cv2.COLOR_RGB2HSV)

        red_mask = cv2.bitwise_or(
            cv2.inRange(hsv, np.array(RED_RANGES_HSV[0][0]), np.array(RED_RANGES_HSV[0][1])),
            cv2.inRange(hsv, np.array(RED_RANGES_HSV[1][0]), np.array(RED_RANGES_HSV[1][1]))
        )

        if np.sum(red_mask == 255) > 0.7 * total:
            return "Red"

        for color, (low, high) in COLOR_RANGES_HSV.items():
            mask = cv2.inRange(hsv, np.array(low), np.array(high))
            if np.sum(mask == 255) > 0.7 * total:
                return color

        return "Unknown"

    def _annotate(self, frame):
        cv2.line(frame, (150, 0), (150, 500), (255, 0, 0), 2)

        cv2.putText(
            frame,
            f"Count: {len(self.counted_ids)}",
            (450, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        return frame

    def _insert_into_db(self, status, color):
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute(
                "INSERT INTO products (status, color, created_at) VALUES (?, ?, ?)",
                (status, color, datetime.datetime.now())
            )

            db.commit()
            db.close()

        except Exception as e:
            logging.error(f"DB error: {e}")


# ─────────────────────────────
# STREAM GENERATOR
# ─────────────────────────────
def gen_frames_direct(vision_system):
    while True:
        frame = vision_system.get_frame()

        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                "WAITING CAMERA...",
                (100, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + 
            buffer.tobytes() + 
            b"\r\n"
        )

        time.sleep(1 / 30)

import cv2
import datetime
import numpy as np
from ultralytics import YOLO
import threading

from database.db import get_db

color_ranges_hsv = {
    "Red": ([0, 100, 100], [10, 255, 255]),
    "Red2": ([160, 100, 100], [180, 255, 255]),
    "Green": ([40, 50, 50], [80, 255, 255]),
    "Blue": ([100, 50, 50], [130, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255]),
}


class VisionSystem:

    def __init__(self, motor_controller):
        self.model = YOLO("yolov8n.pt")
        self.motor_controller = motor_controller
        self.counted_ids = set()
        self.running = False

    # ==========================
    # Start Camera Thread
    # ==========================
    def start(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    # ==========================
    # Main Loop
    # ==========================
    def run(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            result = self.model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False
            )[0]

            if result.boxes.id is None:
                continue

            ids = result.boxes.id.int().cpu().tolist()
            boxes = result.boxes.xyxy.cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()

            for box, obj_id, cls in zip(boxes, ids, classes):

                x1, y1, x2, y2 = map(int, box)
                center_x = (x1 + x2) // 2

                if center_x <= 150 and obj_id not in self.counted_ids:

                    self.counted_ids.add(obj_id)

                    crop = frame[y1:y2, x1:x2]
                    color = self.detect_color(crop)

                    # 👇 هنا القرار
                    if cls == 0:  # مثال: class 0 = OK
                        status = "OK"
                    else:
                        status = "NOT_OK"
                        self.motor_controller.run_pusher(3)

                    self.insert_into_db(status, color)

        cap.release()

    # ==========================
    # Detect Color
    # ==========================
    def detect_color(self, obj):
        dominant_color = "Unknown"
        total_pixels = obj.shape[0] * obj.shape[1]
        hsv = cv2.cvtColor(obj, cv2.COLOR_BGR2HSV)

        for color, (lower, upper) in color_ranges_hsv.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            if np.sum(mask == 255) > 0.7 * total_pixels:
                dominant_color = color

        return dominant_color

    # ==========================
    # Insert Into DB
    # ==========================
    def insert_into_db(self, status, color):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO products (status, color, created_at)
            VALUES (?, ?, ?)
        """, (status, color, datetime.datetime.now()))

        db.commit()
        db.close()

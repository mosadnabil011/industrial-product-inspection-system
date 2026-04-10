import threading, cv2, datetime, numpy as np
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

model = YOLO("yolov8n.pt")
motor_controller = None
counted_ids = set()
running = False


def start():
    """Start Camera Thread"""
    global running
    running = True
    threading.Thread(target=run, daemon=True).start()


def update():
    cap = cv2.VideoCapture(0)

    while running:
        ret, frame = cap.read()
        if not ret:
            continue

        result = model.track(
            frame, persist=True, tracker="bytetrack.yaml", verbose=False
        )[0]

        boxes, ids, classes = [], [], []

        if result.boxes.id is not None:
            ids = result.boxes.id.int().cpu().tolist()
            boxes = result.boxes.xyxy.cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()

        for box, id, cls in zip(boxes, ids, classes):
            x1, y1, x2, y2 = map(int, box)
            centerx = (x1 + x2) // 2

            if centerx <= 150 and id not in counted_ids:
                counted_ids.add(id)
                color = detect_color(frame[y1:y2, x1:x2])
                insert_into_db(model.names[cls], color)
                if cls != 0:
                    motor_controller.run_pusher(3)

        show_annotated_frame(result.plot())

    cap.release()
    cv2.destroyAllWindows()


def detect_color(obj: cv2.typing.MatLike) -> str:
    """Detect Color"""
    dominant_color = "Unknown"
    total_pixels = obj.shape[0] * obj.shape[1]
    hsv = cv2.cvtColor(obj, cv2.COLOR_BGR2HSV)

    red_mask = cv2.bitwise_or(
        cv2.inRange(
            hsv, np.array(RED_RANGES_HSV[0][0]), np.array(RED_RANGES_HSV[0][1])
        ),
        cv2.inRange(
            hsv, np.array(RED_RANGES_HSV[1][0]), np.array(RED_RANGES_HSV[1][1])
        ),
    )
    if np.sum(red_mask == 255) > 0.7 * total_pixels:
        return "Red"

    for color, (lower, upper) in COLOR_RANGES_HSV.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        if np.sum(mask == 255) > 0.7 * total_pixels:
            dominant_color = color
    return dominant_color


def show_annotated_frame(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    cv2.line(frame, (150, 0), (150, 500), (255, 0, 0), 1)
    cv2.putText(
        frame,
        f"Count:{len(counted_ids)}",
        (550, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return frame


def insert_into_db(status: str, color: str) -> None:
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO products (status, color, created_at)
        VALUES (?, ?, ?)
    """,
        (status, color, datetime.datetime.now()),
    )
    db.commit()
    db.close()

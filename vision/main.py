import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import cv2, datetime, numpy as np
from ultralytics import YOLO

color_ranges_hsv = {
    "Red": ([0, 100, 100], [10, 255, 255]),
    "Red ": ([160, 100, 100], [180, 255, 255]),
    "Green": ([40, 50, 50], [80, 255, 255]),
    "Blue": ([100, 50, 50], [130, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255]),
}


def main():
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")

    counted_items = set()
    ids = []
    boxes = []
    classes = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = model.track(
            frame, persist=True, tracker="bytetrack.yaml", verbose=False
        )[0]

        if result.boxes.id is not None:
            ids = result.boxes.id.int().cpu().tolist()
            boxes = result.boxes.xyxy.cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()

        annotated_frame = result.plot()

        cv2.line(annotated_frame, (150, 0), (150, 500), (255, 0, 0), 1)

        for box, id, cls in zip(boxes, ids, classes):
            x_start, y_start, x_end, y_end = box
            if 0 < (x_start + x_end) // 2 <= 150:  # and id not in counted_items:
                counted_items.add(id)
                color = detect_color(
                    frame[int(y_start) : int(y_end), int(x_start) : int(x_end)]
                )
                insert_into_db(cls, color, datetime.datetime.now())

        cv2.putText(
            annotated_frame,
            f"Count:{len(counted_items)}",
            (550, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow("Live", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_color(obj):
    dominant_color = "Unkown"
    total_pixels = obj.shape[1] * obj.shape[0]
    obj = cv2.cvtColor(obj, cv2.COLOR_BGR2HSV)

    for color, (lower, upper) in color_ranges_hsv.items():
        mask = cv2.inRange(obj, np.array(lower), np.array(upper))
        if np.sum(mask == 255) > (0.75 * total_pixels):
            dominant_color = color

    obj = cv2.cvtColor(obj, cv2.COLOR_HSV2BGR)
    cv2.imwrite("detected object.png", obj)

    return dominant_color


def insert_into_db(*args):
    print(*args)
    pass


if __name__ == "__main__":
    main()

import time
import cv2
import numpy as np


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

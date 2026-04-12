
import cv2
import numpy as np

COLOR_RANGES_HSV = {
    "Green": ([40, 50, 50], [80, 255, 255]),
    "Blue": ([100, 50, 50], [130, 255, 255]),
    "Yellow": ([20, 100, 100], [30, 255, 255]),
}
RED_RANGES_HSV = (
    ([0, 100, 100], [10, 255, 255]),
    ([160, 100, 100], [180, 255, 255]),
)


def detect_color(obj) -> str:
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
        if np.sum(mask == 255) > 0.5 * total_pixels:
            dominant_color = color
    return dominant_color


if __name__ == "__main__":

    print (detect_color(cv2.imread("WhatsApp Image 2026-03-18 at 11.32.13 AM.jpeg")))
    print (detect_color(cv2.imread("WhwwwatsApp Image 2026-03-18 at 11.32.13 AM.jpeg")))
    
    
import cv2

def gen_frames():
    cap = cv2.VideoCapture(0)  # كاميرا 0
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # هنا ممكن ترسم أو تضيف annotate بالفريم
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
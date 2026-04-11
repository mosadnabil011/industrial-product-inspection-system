# Smart Production Line Inspector

**Graduation Project — Computer Engineering**

Stack: `Python` · `Flask` · `YOLOv8` · `OpenCV` · `Raspberry Pi` · `SQLite`

---

## System Architecture

### High-Level Architecture — Horizontal View

The system is organised into four layers: **Acquisition** (camera + conveyor), **Inference** (Raspberry Pi running YOLOv8), **Actuation** (GPIO relay-controlled motors and pusher mechanism), and **Monitoring** (web dashboard with live video, counters, and motor controls).

![High-Level System Architecture](arch1.png)

### Data Flow & Component Interaction

Products on Conveyor Belt 1 pass under the camera. The Raspberry Pi classifies each item using YOLOv8 and triggers control commands via GPIO/Relay. Defective items are diverted to Conveyor Belt 2 (Reject Line). Detection results are stored in the database and surfaced through the REST API and web dashboard.

![Data Flow and Component Interaction](arch2.png)

---

## 1. Overview

This system automates quality inspection on a conveyor belt production line. A camera mounted above the belt feeds live video into a YOLOv8 object-detection model. Each detected product is classified and its dominant colour identified. Defective products (any class other than class 0) trigger a pusher motor that diverts them off the main belt. All results are recorded in a local SQLite database and visualised in a real-time web dashboard.

### Key capabilities

- Real-time object detection & tracking with YOLOv8n + ByteTrack
- HSV-based colour detection (Red, Green, Blue, Yellow, Unknown)
- Relay-controlled motors via Raspberry Pi GPIO (gpiozero)
- Physical push-buttons and emergency-stop button wired to GPIO
- Live MJPEG video stream in the browser
- REST API for motor control and production statistics
- Dark-mode responsive dashboard (Bootstrap 5)
- Export production data to PDF (ReportLab) or Excel (pandas)

---

## 2. Hardware Requirements

- Raspberry Pi 4 (2 GB RAM minimum recommended)
- USB webcam or Raspberry Pi Camera Module v2
- 3-channel relay module (active LOW)
- 3 DC motors — Main belt, Bad/reject belt, Pusher
- 2 push-buttons (Main toggle GPIO 17, Bad toggle GPIO 27)
- 1 emergency-stop button (GPIO 22)
- Suitable power supply for motors (external, not from Pi)

---

## 3. Project Structure

```
graduation-project/
│
├── app.py                      # Flask app factory — wires all components together
├── requirements.txt            # Python dependencies
├── yolov8n.pt                  # Pre-trained YOLOv8 nano model weights
├── Production_DB.db            # SQLite database (auto-created on first run)
│
├── vision/
│   ├── detector.py             # VisionSystem class — camera loop, YOLO tracking, color detection
│   └── stream.py               # MJPEG frame generator for /video_feed route
│
├── gpio/
│   └── controller.py           # MotorController — relay logic, buttons, emergency stop
│
├── routes/
│   ├── control.py              # REST API blueprint — toggle motors, run pusher, emergency
│   └── stats.py                # REST API blueprint — production summary statistics
│
├── database/
│   ├── db.py                   # SQLite connection helper + init_db()
│   ├── models.py               # CREATE TABLE statement for products
│   └── insert_dummy.py         # Script to seed 50 random rows for testing
│
├── export/
│   ├── PDF.py                  # Route to export production report as PDF (ReportLab)
│   └── Excel.py                # Route to export production data as Excel (pandas)
│
├── templates/
│   └── dashboard.html          # Single-page dashboard — Control / Dashboard / Reports
│
└── static/
    ├── js/main.js              # Frontend JS — motor toggles, stats polling, dark mode
    └── css/style.css           # Dashboard styles
```

---

## 4. Installation

### 4.1 Clone the repository

```bash
git clone https://github.com/mosadnabil011/graduation-project.git
cd graduation-project
```

### 4.2 Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 4.3 Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `RPi.GPIO` / `gpiozero` are only required on a real Raspberry Pi. On other platforms the GPIO lines raise `ImportError` — mock them or run without hardware.

### 4.4 Install additional dependencies for exports (optional)

```bash
pip install pandas openpyxl reportlab
```

### 4.5 Verify the YOLOv8 model file

The file `yolov8n.pt` must exist in the project root. If missing, download it:

```bash
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## 5. Configuration

All hardware pin assignments live in `gpio/controller.py`:

```python
self.motors = {
    "main":   {"relay_pin": 23, "button_pin": 17},
    "bad":    {"relay_pin": 24, "button_pin": 27},
    "pusher": {"relay_pin": 25, "button_pin": None},
}
self.emergency_button_pin = 22
```

The detection trigger line (default x ≤ 150 pixels from left) can be adjusted in `vision/detector.py`:

```python
if centerx <= 150 and obj_id not in self.counted_ids:
```

---

## 6. Running the Application

```bash
python app.py
```

The server starts on all interfaces at port 5000. Open a browser on the same network:

```
http://<raspberry-pi-ip>:5000
```

To find the Pi's IP address:

```bash
hostname -I
```

---

## 7. REST API Reference

### 7.1 Motor Control — `/api/control`

| Endpoint | Method | Description |
|---|---|---|
| `/api/control/toggle-main` | `POST` | Toggle the main conveyor motor ON/OFF |
| `/api/control/toggle-bad` | `POST` | Toggle the reject belt motor ON/OFF |
| `/api/control/run-pusher` | `POST` | Run the pusher motor for 8 seconds |
| `/api/control/stop-pusher` | `POST` | Stop the pusher motor immediately |
| `/api/control/emergency` | `POST` | EMERGENCY STOP — stops all motors instantly |
| `/api/control/status` | `GET` | Returns JSON with current state of all motors |

### 7.2 Statistics — `/api/stats`

| Endpoint | Method | Description |
|---|---|---|
| `/api/stats/summary` | `GET` | Returns total OK, NOT_OK counts and breakdown by colour |

### 7.3 Video Stream

| Endpoint | Method | Description |
|---|---|---|
| `/video_feed` | `GET` | MJPEG live stream — embed as `<img src="/video_feed" />` |

---

## 8. Database Schema

SQLite file: `Production_DB.db` — created automatically on first run.

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | INTEGER | AUTOINCREMENT | Primary key |
| `status` | TEXT | — | YOLO class name (e.g. `OK`, `NOT_OK`) |
| `color` | TEXT | — | Detected colour (Red, Green, Blue, Yellow, Unknown) |
| `created_at` | DATETIME | CURRENT_TIMESTAMP | Timestamp of detection |

To seed 50 random rows for testing:

```bash
python database/insert_dummy.py
```

---

## 9. Dashboard

The single-page dashboard is served at `/` and has three sections:

- **Control Panel** — toggle Main belt, Bad belt, and Pusher motor. One-click Emergency Stop card stops everything immediately.
- **Dashboard** — live counters for Total / Valid / Invalid boxes and Defect Rate %. Charts area (work in progress).
- **Reports** — export buttons for PDF and Excel (requires optional dependencies).

The frontend polls `/api/control/status` and `/api/stats/summary` every 1 second. Dark mode toggle persists across sessions via `localStorage`.

To display the live video stream in the dashboard, add this inside the Live card in `dashboard.html`:

```html
<img src="/video_feed" style="max-height:100%; max-width:100%; object-fit:contain;" />
```

---

## 10. Troubleshooting

### Camera not found
- Check the camera index in `vision/detector.py`: `cv2.VideoCapture(0)`. Try index `1` or `2` if you have multiple cameras.
- On Raspberry Pi with the CSI camera: `sudo modprobe bcm2835-v4l2`

### GPIO errors on non-Raspberry Pi machines
- `gpiozero` raises `DeviceNotFoundError` if no GPIO hardware is present.
- Comment out `MotorController()` in `app.py` and pass a mock object to `VisionSystem` for development without hardware.

### No video in the browser
- Confirm `/video_feed` returns data: `curl http://localhost:5000/video_feed | head -c 200`
- Make sure `VISION_SYSTEM` is set on `app.config` (done automatically in `app.py`).
- Check that the `<img>` tag in `dashboard.html` points to `/video_feed`.

### `counted_ids` growing indefinitely
- The set is capped at `MAX_TRACKED_IDS = 500` in `vision/detector.py` and clears automatically when that limit is reached.

---

## 11. Known Limitations & Future Work

- The Dashboard chart slots (cards 1, 2, 3) are placeholders — Chart.js integration is pending.
- The Reports section UI is empty — export routes exist in `export/` but are not yet wired to the blueprint.
- SQLite is single-writer; under very high detection rates a queue should buffer DB inserts.
- The MJPEG stream uses ~30 fps polling; adaptive frame rate based on CPU load would improve performance.
- No authentication on the API — consider adding Flask-Login before deploying on a network.

---

## 12. License

This project was developed as a graduation project and is shared for educational purposes. All rights reserved by the authors unless otherwise stated.

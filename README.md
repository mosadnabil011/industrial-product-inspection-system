# FORCE — Industrial Product Inspection System

> **Graduation Project — Computer Engineering**

A real-time automated quality control system built for conveyor belt production lines. The system uses a camera, YOLOv8 object detection, and Raspberry Pi GPIO to classify products, detect defects, and physically divert rejected items — all visible through a live web dashboard.

**Stack:** `Python` · `Flask` · `YOLOv8` · `OpenCV` · `picamera2` · `SQLite` · `gpiozero` · `ReportLab`

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [System Architecture](#2-system-architecture)
3. [Hardware Requirements](#3-hardware-requirements)
4. [Project Structure](#4-project-structure)
5. [Installation](#5-installation)
6. [Configuration](#6-configuration)
7. [Running the Application](#7-running-the-application)
8. [REST API Reference](#8-rest-api-reference)
9. [Database Schema](#9-database-schema)
10. [Dashboard](#10-dashboard)
11. [PDF Report Generation](#11-pdf-report-generation)
12. [Troubleshooting](#12-troubleshooting)
13. [Known Limitations & Future Work](#13-known-limitations--future-work)
14. [Project Documentation](#14-project-documentation)
15. [License](#15-license)

---

## 1. System Overview

FORCE automates quality inspection on a conveyor belt production line:

1. A Raspberry Pi Camera Module captures live video of products on the belt.
2. A **YOLOv8** model (`best.pt`) detects and tracks each product using **ByteTrack**.
3. Each product's dominant colour is identified via **HSV-based colour detection** (Red, Green, Blue, Yellow).
4. Products classified as defective (any class other than `OK`) trigger a **pusher motor** via GPIO relay to divert them off the main belt.
5. All detections are saved to a **SQLite** database.
6. A **Flask** web dashboard shows live video, counters, motor controls, and allows exporting PDF reports.

### Key Capabilities

- Real-time object detection & ID tracking with YOLOv8 + ByteTrack
- HSV colour detection: Red, Green, Blue, Yellow, Unknown
- Relay-controlled motors through Raspberry Pi GPIO (gpiozero)
- Physical start button and emergency-stop button wired to GPIO
- Live MJPEG video stream embedded in the browser
- REST API for motor control and production statistics (summary, monthly, weekly)
- Dark-mode responsive web dashboard (Bootstrap 5)
- Automated PDF production reports with charts (ReportLab + Matplotlib)

---

## 2. System Architecture

### High-Level Architecture

The system is organised into four layers:

| Layer           | Components                                                          |
| --------------- | ------------------------------------------------------------------- |
| **Acquisition** | Raspberry Pi Camera (picamera2), Conveyor Belt                      |
| **Inference**   | YOLOv8n model (`best.pt`), ByteTrack, HSV colour detection          |
| **Actuation**   | GPIO relay module, Main motor, Bad/reject motor, Pusher, Back-motor |
| **Monitoring**  | Flask REST API, Live MJPEG stream, Web dashboard, SQLite DB         |

### Data Flow

```
Camera → picamera2 frame → YOLOv8 track()
       → [Object detected at x ≤ 150px trigger line]
              ├─→ Color detection (HSV)
              ├─→ INSERT INTO products (status, color, created_at)
              └─→ if defective → GPIO relay → Pusher motor fires
                                           → Back-motor resets pusher
```

---

## 3. Hardware Requirements

| Component          | Details                                                            |
| ------------------ | ------------------------------------------------------------------ |
| **Raspberry Pi 4** | 2 GB RAM minimum recommended                                       |
| **Camera**         | Raspberry Pi Camera Module v2 (CSI connector, used via picamera2)  |
| **Relay Module**   | 4-channel active-LOW relay                                         |
| **Motors**         | 4 DC motors: Main belt, Bad/reject belt, Pusher, Back-motor pusher |
| **Buttons**        | Start button (GPIO 21), Emergency stop (GPIO 20)                   |
| **Power**          | External motor power supply (do NOT power motors from the Pi)      |

### GPIO Pin Assignment

| Signal                  | GPIO BCM Pin |
| ----------------------- | ------------ |
| Main belt relay         | 23           |
| Bad belt relay          | 24           |
| Pusher relay            | 25           |
| Back-motor pusher relay | 5            |
| Start button            | 21           |
| Emergency stop          | 20           |

> All relay channels are **active LOW** — `relay.on()` = motor OFF, `relay.off()` = motor ON.

---

## 4. Project Structure

```
industrial-product-inspection-system/
│
├── app.py                      # Flask app factory — wires all components
├── requirements.txt            # Python dependencies
├── best.pt                     # Custom-trained YOLOv8 model weights
├── start_app.sh                # Shell script to launch the app with logging
├── Production_DB.db            # SQLite database (auto-created on first run)
│
├── vision/
│   ├── detector.py             # VisionSystem — camera loop, YOLO tracking, colour detection
│   └── stream.py               # MJPEG frame generator for /video_feed route
│
├── gpio/
│   └── controller.py           # MotorController — relay logic, pusher sequence, buttons
│
├── routes/
│   ├── control.py              # API blueprint — toggle motors, emergency stop, status
│   ├── stats.py                # API blueprint — summary, monthly, weekly stats
│   └── report.py               # API blueprint — PDF report generation
│
├── database/
│   ├── db.py                   # SQLite connection helper + init_db()
│   ├── models.py               # CREATE TABLE for products
│   └── insert_dummy.py         # Seeds 50 random rows for testing
│
├── templates/
│   ├── login.html              # Login page (served at / and /login.html)
│   └── dashboard.html          # Main SPA — Control / Dashboard / Reports
│
├── static/
│   ├── js/                     # Frontend JavaScript
│   └── css/                    # Dashboard styles
│
└── docs/
    ├── paper.pdf               # Graduation project academic paper
    └── report.pdf              # Project technical report
```

---

## 5. Installation

### 5.1 Clone the Repository

```bash
git clone https://github.com/mosadnabil011/industrial-product-inspection-system.git
cd industrial-product-inspection-system
```

### 5.2 Create a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` installs:

```
flask==2.3.2
ultralytics          # YOLOv8
opencv-python-headless
numpy
```

### 5.4 Install GPIO & Camera Libraries (Raspberry Pi Only)

```bash
pip install gpiozero picamera2 --break-system-packages
```

> **Note:** `gpiozero` and `picamera2` are Raspberry Pi specific. On other platforms the camera and GPIO lines raise `ImportError`. Mock them for development without hardware (see [Troubleshooting](#12-troubleshooting)).

### 5.5 Install Report Dependencies

```bash
pip install reportlab matplotlib flask-cors
```

### 5.6 Verify the YOLOv8 Model File

The file `best.pt` must exist in the project root. This is the custom-trained model specific to this project. Confirm it is present:

```bash
ls -lh best.pt
```

---

## 6. Configuration

### Detection Trigger Line

Products are counted and classified when their bounding-box center-X crosses the trigger line at **x = 150 pixels**. Adjust in `vision/detector.py`:

```python
if centerx <= 150 and obj_id not in self.counted_ids:
```

To change the trigger position, replace `150` with the desired pixel value.

### Colour Detection Thresholds

HSV ranges for each colour are defined at the top of `vision/detector.py`:

```python
COLOR_RANGES_HSV = {
    "Green":  ([40,  50,  50],  [80,  255, 255]),
    "Blue":   ([100, 50,  50],  [130, 255, 255]),
    "Yellow": ([20,  100, 100], [30,  255, 255]),
}
# Red uses two ranges (wraps around 0°/180°)
RED_RANGES_HSV = (
    ([0,   100, 100], [10,  255, 255]),
    ([160, 100, 100], [180, 255, 255]),
)
```

A colour is detected when it covers **more than 20%** of the product's bounding box area.

### GPIO Pin Assignments

All pin assignments live in `gpio/controller.py`:

```python
self.motors = {
    "main":               {"relay_pin": 23},
    "bad":                {"relay_pin": 24},
    "pusher":             {"relay_pin": 25},
    "back_motor_pusher":  {"relay_pin": 5},
}
self.start_button_pin     = 21
self.emergency_button_pin = 20
```

### Pusher Timing

The pusher sequence in `gpio/controller.py → run_pusher()`:

| Step                     | Duration |
| ------------------------ | -------- |
| Pusher extends           | 0.1 s    |
| Wait before back-motor   | 1 s      |
| Back-motor resets pusher | 0.2 s    |

### Tracked ID Memory

To prevent double-counting, each object's ByteTrack ID is stored in `counted_ids`. The set is capped at `MAX_TRACKED_IDS = 500` (defined in `vision/detector.py`) and resets automatically when full.

### Flask Secret Key

Change the default secret key before deploying:

```python
# app.py
app.config["SECRET_KEY"] = "your-secure-secret-key-here"
```

---

## 7. Running the Application

### Direct Launch

```bash
python3 app.py
```

### Using the Shell Script (with logging)

```bash
chmod +x start_app.sh
./start_app.sh
```

Logs are written to `logs/app.log`.

### Access the Dashboard

The server starts on all interfaces at port **5000**. Open a browser:

```
http://<raspberry-pi-ip>:5000
```

Find the Pi's IP address:

```bash
hostname -I
```

---

## 8. REST API Reference

### 8.1 Motor Control — `/api/control`

| Endpoint                   | Method | Description                                     |
| -------------------------- | ------ | ----------------------------------------------- |
| `/api/control/toggle-main` | `POST` | Toggle main conveyor motor ON/OFF               |
| `/api/control/toggle-bad`  | `POST` | Toggle reject belt motor ON/OFF                 |
| `/api/control/run-pusher`  | `POST` | Run pusher sequence (extend → wait → retract)   |
| `/api/control/stop-pusher` | `POST` | Stop pusher immediately                         |
| `/api/control/emergency`   | `POST` | **EMERGENCY STOP** — stops all motors instantly |
| `/api/control/status`      | `GET`  | Returns JSON with current state of all motors   |

**Example response — `/api/control/status`:**

```json
{
  "main": false,
  "bad": false,
  "pusher": false,
  "back_motor_pusher": false
}
```

### 8.2 Statistics — `/api/stats`

| Endpoint             | Method | Description                                       |
| -------------------- | ------ | ------------------------------------------------- |
| `/api/stats/summary` | `GET`  | Total OK/NOT_OK counts + breakdown by colour      |
| `/api/stats/monthly` | `GET`  | Monthly valid/invalid counts grouped by `YYYY-MM` |
| `/api/stats/weekly`  | `GET`  | Weekly valid/invalid counts grouped by `YYYY-WNN` |

**Example response — `/api/stats/summary`:**

```json
{
  "ok": 142,
  "not_ok": 18,
  "colors": {
    "Red": 55,
    "Green": 62,
    "Blue": 30,
    "Yellow": 10,
    "Unknown": 3
  }
}
```

**Example response — `/api/stats/monthly`:**

```json
{
  "months": ["2025-01", "2025-02"],
  "valid": [80, 62],
  "invalid": [10, 8]
}
```

### 8.3 Report — `/api/report`

| Endpoint      | Method | Query Param       | Description                                 |
| ------------- | ------ | ----------------- | ------------------------------------------- |
| `/api/report` | `GET`  | `date=YYYY-MM-DD` | Generate and download PDF production report |

**Example:**

```
GET /api/report?date=2025-01-01
```

Returns a PDF file named `FORCE_Report_<date>.pdf`.

### 8.4 Video Stream

| Endpoint      | Method | Description                  |
| ------------- | ------ | ---------------------------- |
| `/video_feed` | `GET`  | Live MJPEG stream at ~30 fps |

Embed in HTML:

```html
<img src="/video_feed" style="max-width:100%; object-fit:contain;" />
```

---

## 9. Database Schema

**File:** `Production_DB.db` (SQLite, auto-created on first run)

**Table:** `products`

| Column       | Type     | Default             | Description                                        |
| ------------ | -------- | ------------------- | -------------------------------------------------- |
| `id`         | INTEGER  | AUTOINCREMENT       | Primary key                                        |
| `status`     | TEXT     | —                   | YOLO class name: `OK` or `NOT_OK`                  |
| `color`      | TEXT     | —                   | Detected colour: Red, Green, Blue, Yellow, Unknown |
| `created_at` | DATETIME | `CURRENT_TIMESTAMP` | Detection timestamp                                |

### Seed Test Data

```bash
python3 database/insert_dummy.py
```

Inserts 50 random rows for UI testing.

---

## 10. Dashboard

The single-page dashboard is served at `/dashboard.html` and has three sections:

### Control Panel

- Toggle **Main Belt**, **Bad Belt**, and **Pusher** motors individually.
- One-click **Emergency Stop** card stops all motors instantly.
- Motor state is polled from `/api/control/status` every second.

### Dashboard (Stats)

- Live counters: **Total**, **Valid**, **Invalid**, **Defect Rate %**.
- Monthly and weekly chart views powered by Chart.js.
- Stats polled from `/api/stats/summary`, `/api/stats/monthly`, `/api/stats/weekly` every second.
- Live annotated video stream from `/video_feed`.

### Reports

- Date picker to select the reporting period start date.
- **Export PDF** button calls `/api/report?date=<selected>` and opens the PDF.

---

## 11. PDF Report Generation

The `/api/report` endpoint generates a professional A4 PDF using **ReportLab** and **Matplotlib**, including:

- **KPI cards:** Total, Valid, Invalid, Pass Rate %, Defect Rate %
- **Monthly production table** with PASS/FAIL/REVIEW status
- **Pie chart:** Quality distribution (Valid vs Invalid)
- **Bar chart:** Month-by-month comparison
- Branded header (FORCE logo area + report title) and footer with page numbers

The PDF is streamed directly to the browser (no file saved on disk).

---

## 12. Troubleshooting

### Camera not found / `picamera2` error

The system uses `picamera2` (CSI camera only). Make sure the camera is enabled:

```bash
sudo raspi-config   # Interface Options → Camera → Enable
```

Verify the camera is detected:

```bash
libcamera-hello
```

If `picamera2` is not installed:

```bash
pip install picamera2 --break-system-packages
```

### GPIO errors on non-Raspberry Pi machines

`gpiozero` raises `DeviceNotFoundError` if no GPIO hardware is present. For development without hardware, comment out the GPIO and camera sections in `app.py` and pass a mock object:

```python
# For development only — mock MotorController
class MockMotor:
    def run_pusher(self): pass
    def get_status(self): return {}

motor_controller = MockMotor()
```

### No video in the browser

1. Check `/video_feed` directly: `curl http://localhost:5000/video_feed | head -c 200`
2. Confirm `VISION_SYSTEM` is set: it is stored in `app.config["VISION_SYSTEM"]` automatically.
3. If the camera loop failed to start, check `logs/app.log` for `picamera2` errors.

### Double-counting products

If products are being counted more than once, the trigger line (`centerx <= 150`) may be positioned where the object lingers. Adjust the pixel value or add a cooldown period.

### `counted_ids` set grows large

The set is capped at `MAX_TRACKED_IDS = 500` and resets automatically. No action needed for normal operation; adjust the cap in `vision/detector.py` if needed.

### Database locked error

SQLite is single-writer. If multiple threads insert simultaneously, you may see lock errors. The current implementation opens and closes a new connection per detection event. For high-throughput lines, consider adding a queue-based insertion worker.

### Port 5000 already in use

```bash
# Find and kill the process using port 5000
sudo lsof -t -i:5000 | xargs kill -9
```

---

## 13. Known Limitations & Future Work

| Area            | Current State               | Suggested Improvement                        |
| --------------- | --------------------------- | -------------------------------------------- |
| Authentication  | No login on API endpoints   | Add Flask-Login before network deployment    |
| Database writes | Synchronous, per-detection  | Queue-based async writer for high throughput |
| Camera          | CSI camera only (picamera2) | Add USB webcam fallback via OpenCV           |
| MJPEG stream    | Fixed ~30 fps               | Adaptive frame rate based on CPU load        |
| Report          | Monthly aggregation only    | Add daily drill-down and colour breakdown    |
| Model           | Single `best.pt` file       | Add model hot-swap endpoint                  |
| Pusher timing   | Fixed 0.1 s / 1 s / 0.2 s   | Expose timing via config file                |

---

## 14. Project Documentation

| Document         | Path                                 |
| ---------------- | ------------------------------------ |
| Academic Paper   | [`docs/paper.pdf`](docs/paper.pdf)   |
| Technical Report | [`docs/report.pdf`](docs/report.pdf) |

---

## 15. Acknowledgements

This project was supervised by **Prof. Mohamed Moawad**, whose guidance, technical feedback, and continuous support throughout the development process were instrumental in bringing this system to completion.

We would also like to thank the Computer Engineering Department for providing the resources and environment necessary to carry out this graduation project.

---

## 16. License

This project was developed as a graduation project and is shared for educational purposes. All rights reserved by the authors unless otherwise stated.

from flask import Flask, render_template, Response
from database.db import init_db
from gpio.controller import MotorController
from routes.control import init_control_routes
from routes.stats import stats_bp
import logging
from vision.detector import VisionSystem
from flask_cors import CORS
from vision.stream import gen_frames_direct
from routes.report import report_bp 
logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "graduation-project-secret"

    # ── Database ──────────────────────────────────────────────────────────
    try:
        init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")

    # ── Motor Controller ──────────────────────────────────────────────────
    motor_controller = MotorController()

    # ── Vision System ─────────────────────────────────────────────────────
    vision_system = VisionSystem(motor_controller)
    vision_system.start()

    # Store on app.config so gen_frames() can reach it without a circular import
    app.config["VISION_SYSTEM"] = vision_system

    # ── Blueprints ────────────────────────────────────────────────────────
    app.register_blueprint(
        init_control_routes(motor_controller),
        url_prefix="/api/control",
    )
    app.register_blueprint(stats_bp, url_prefix="/api/stats")

    app.register_blueprint(report_bp, url_prefix="/api")

    # ── Routes ────────────────────────────────────────────────────────────
    @app.route("/video_feed")
    def video_feed():
        vision_system = app.config["VISION_SYSTEM"]

        return Response(
            gen_frames_direct(vision_system),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/login.html")
    def login():
        return render_template("login.html")

    @app.route("/dashboard.html")
    def dashboard_page():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    CORS(app)
    app.run(host="0.0.0.0", port=5000, threaded=True)

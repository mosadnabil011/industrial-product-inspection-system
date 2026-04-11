from flask import Flask, render_template , Response
from database.db import init_db
from gpio.controller import MotorController
from routes.control import init_control_routes
from routes.stats import stats_bp
import logging
from vision.detector import VisionSystem
from flask_cors import CORS
from vision.stream import gen_frames
logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "graduation-project-secret"

    # ===============================
    # Init database safely
    # ===============================
    try:
        init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")

    # ===============================
    # Init Motor Controller
    # ===============================
    motor_controller = MotorController()
    # ===============================
    # Init Vision System
    # ===============================
    vision_system = VisionSystem(motor_controller)
    vision_system.start()
    # ===============================
    # Register Blueprints
    # ===============================
    app.register_blueprint(
        init_control_routes(motor_controller),
        url_prefix="/api/control"
    )
    app.register_blueprint(
        stats_bp,
        url_prefix="/api/stats"
    )

    # ===============================
    #  Video Stream Route
    # ===============================
    @app.route("/video_feed")
    def video_feed():
        return Response(
            gen_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    # ===============================
    # Dashboard
    # ===============================
    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    for rule in app.url_map.iter_rules():
        print(rule)
    CORS(app)
    app.run(host="0.0.0.0", port=5000)

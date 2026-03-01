from flask import Flask, render_template

# ===============================
# Blueprints
# ===============================
from routes.control import control_bp
from routes.stats import stats_bp

# ===============================
# DB Init
# ===============================
from database.db import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "graduation-project-secret"

    # Init database
    init_db()

    # Register Blueprints
    app.register_blueprint(control_bp, url_prefix="/api/control")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")

    # Dashboard
    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
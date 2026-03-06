from flask import Blueprint, jsonify

control_bp = Blueprint("control", __name__)

def init_control_routes(motor_controller):

    @control_bp.route("/toggle-main", methods=["POST"])
    def toggle_main_line():
        state = motor_controller.toggle_motor("main")
        return jsonify({
            "main_motor": state
        }), 200


    @control_bp.route("/toggle-bad", methods=["POST"])
    def toggle_bad_line():
        state = motor_controller.toggle_motor("bad")
        return jsonify({
            "bad_motor": state
        }), 200

    @control_bp.route("/toggle-pusher", methods=["POST"])
    def toggle_pusher_line():
        state = motor_controller.toggle_motor("pusher")
        return jsonify({
            "pusher_motor": state
        }), 200


    @control_bp.route("/emergency", methods=["POST"])
    def emergency():
        status = motor_controller.emergency_stop()
        return jsonify({
            "message": "EMERGENCY STOP ACTIVATED",
            **status
        }), 200


    @control_bp.route("/status", methods=["GET"])
    def status():
        return jsonify(
            motor_controller.get_status()
        ), 200


    return control_bp
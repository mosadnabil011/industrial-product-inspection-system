from flask import Blueprint, jsonify
from gpio.controller import toggle_main, toggle_bad, emergency_stop, get_status

control_bp = Blueprint("control", __name__)

@control_bp.route("/toggle-main")
def toggle_main_line():
    state = toggle_main()
    return jsonify({
        "main_motor": state
    })


@control_bp.route("/toggle-bad")
def toggle_bad_line():
    state = toggle_bad()
    return jsonify({
        "bad_motor": state
    })


@control_bp.route("/emergency")
def emergency():
    status = emergency_stop()
    return jsonify({
        "message": "EMERGENCY STOP ACTIVATED",
        **status
    })


@control_bp.route("/status")
def status():
    return jsonify(get_status())
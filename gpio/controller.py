
from gpiozero import LED, Button
import threading
import time


class MotorController:

    def __init__(self):
        self.lock = threading.Lock()

        # ========================
        # Motor Configuration
        # ========================
        self.motors = {
            "main": {"relay_pin": 23, "button_pin": 17, "state": False},
            "bad": {"relay_pin": 24, "button_pin": 27, "state": False},
            "pusher": {"relay_pin": 25, "button_pin": None, "state": False},
        }

        self.emergency_button_pin = 22

        # ========================
        # Devices Setup
        # ========================
        for name, motor in self.motors.items():

            # relay
            motor["relay"] = LED(motor["relay_pin"])
            motor["relay"].on()  # ensure all motors are OFF at startup

            # button
            if motor["button_pin"] is not None:
                motor["button"] = Button(motor["button_pin"])
                motor["button"].when_pressed = lambda n = name: self.toggle_motor(n)

        # emergency button
        self.emergency_button = Button(self.emergency_button_pin)
        self.emergency_button.when_pressed = self.emergency_stop

    # ========================
    # Dynamic Methods
    # ========================

    def toggle_motor(self, name):
        if name not in self.motors:
            raise ValueError(f"Motor '{name}' not found")

        motor = self.motors[name]
        motor["state"] = not motor["state"]

        # ======== Active LOW ========
        if motor["state"]:
            motor["relay"].off()  # trigger relay to turn ON the motor
        else:
            motor["relay"].on()  # trigger relay to turn OFF the motor

        return motor["state"]

    def emergency_stop(self):
        print("!!! EMERGENCY STOP ACTIVATED !!!")
        for motor in self.motors.values():
            motor["state"] = False
            motor["relay"].on()  # trigger relay to turn OFF all motors
        return self.get_status()

    def run_pusher(self, seconds=8):

        def worker():
            with self.lock:
                motor = self.motors["pusher"]
                if motor["state"]:
                    return
                motor["state"] = True
                motor["relay"].off()  # trigger relay to turn ON the pusher

            time.sleep(seconds)

            with self.lock:
                motor["state"] = False
                motor["relay"].on()  # trigger relay to turn OFF the pusher

        threading.Thread(target=worker, daemon=True).start()

    def get_status(self):
        return {name: motor["state"] for name, motor in self.motors.items()}

    def cleanup(self):
        for motor in self.motors.values():
            motor["relay"].on()  # trigger relay to turn OFF all motors


from gpiozero import LED, Button
import threading
import time


class MotorController:

    def __init__(self):
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        # ========================
        # Motor Configuration
        # ========================
        self.motors = {
            "main": {"relay_pin": 23, "button_pin": 17, "state": False},
            "bad": {"relay_pin": 24, "button_pin": 27, "state": False},
            "pusher": {"relay_pin": 25, "button_pin": None, "state": False},
        }
        
        self.start_button_pin = 21
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
                # motor["button"] = Button(motor["button_pin"])
                motor["button"] = Button(
                        motor["button_pin"],
                        pull_up=True,
                        bounce_time=0.2
                        )
                motor["button"].when_pressed = lambda n = name: self.toggle_motor(n)

        # emergency button
        # self.emergency_button = Button(self.emergency_button_pin)
        self.emergency_button = Button(self.emergency_button_pin)
        self.emergency_button.when_pressed = self.emergency_stop
        # start button
        # self.start_button = Button(self.start_button_pin)
        self.start_button = Button(
            self.start_button_pin,
            pull_up=True,
            bounce_time=0.2
        )
        self.start_button.when_pressed = self.start_system
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

    # ========================
    # EMERGENCY STOP
    # ========================
    def emergency_stop(self):
        print("!!! EMERGENCY STOP ACTIVATED !!!")

        self.stop_event.set()  

        for motor in self.motors.values():
            motor["state"] = False
            motor["relay"].on()

        return self.get_status()
    
    # ========================
    # START SYSTEM
    # ========================
    
    def start_system(self):

        print("SYSTEM STARTED")

        self.stop_event.clear()

        # turn on main
        self.motors["main"]["state"] = True
        self.motors["main"]["relay"].off()

        # turn on bad
        self.motors["bad"]["state"] = True
        self.motors["bad"]["relay"].off()
    
    def run_pusher(self, seconds=8):

        def worker():
            if self.stop_event.is_set():
                return
            with self.lock:
                motor = self.motors["pusher"]
                if motor["state"]:
                    return
                motor["state"] = True
                motor["relay"].off()  # trigger relay to turn ON the pusher

            start_time = time.time()
            while time.time() - start_time < seconds:
                if self.stop_event.is_set():
                    break
                time.sleep(0.1)

            with self.lock:
                motor["state"] = False
                motor["relay"].on()  # trigger relay to turn OFF the pusher

        # self.stop_event.clear()
        threading.Thread(target=worker, daemon=True).start()

    def stop_pusher(self):
        with self.lock:
            motor = self.motors["pusher"]
            self.stop_event.set()  

            motor["state"] = False
            motor["relay"].on()  # OFF

        return motor["state"]
    
    def get_status(self):
        return {name: motor["state"] for name, motor in self.motors.items()}

    def cleanup(self):
        for motor in self.motors.values():
            motor["relay"].on()  # trigger relay to turn OFF all motors

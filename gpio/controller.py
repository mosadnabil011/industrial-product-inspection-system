# gpio/controller.py

# import RPi.GPIO as GPIO
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:

    # Mock GPIO for Windows development
    class MockGPIO:
        BCM = OUT = IN = HIGH = LOW = PUD_DOWN = RISING = None
        
        def setmode(self, *args): pass

        def setup(self, *args, **kwargs): pass

        def output(self, *args): pass

        def add_event_detect(self, *args, **kwargs): pass

        def cleanup(self): pass

    GPIO = MockGPIO()
import threading
import time


class MotorController:

    def __init__(self):
        self.lock = threading.Lock()
        GPIO.setmode(GPIO.BCM)

        # ========================
        # Motor Configuration
        # ========================
        # can add more motors by adding entries here
        self.motors = {
            "main": {"relay": 23, "button": 17, "state": True},
            "bad": {"relay": 24, "button": 27, "state": False},
            "pusher": {"relay": 25, "button": None, "state": False},
        }

        self.emergency_button = 22

        # ========================
        # GPIO Setup
        # ========================
        for name, motor in self.motors.items():
            GPIO.setup(motor["relay"], GPIO.OUT)
            GPIO.output(motor["relay"], GPIO.LOW)

            if motor["button"] is not None:
                GPIO.setup(motor["button"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

                GPIO.add_event_detect(
                    motor["button"],
                    GPIO.RISING,
                    callback=lambda channel, n=name: self.toggle_motor(n),
                    bouncetime=300
                )

        GPIO.setup(self.emergency_button, GPIO.IN,
                    pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(
            self.emergency_button,
            GPIO.RISING,
            callback=self.emergency_stop,
            bouncetime=300
        )

    # ========================
    # Dynamic Methods
    # ========================

    def toggle_motor(self, name):

        if name not in self.motors:
            raise ValueError(f"Motor '{name}' not found")
        motor = self.motors[name]
        motor["state"] = not motor["state"]
        # GPIO.output(motor["relay"], motor["state"])
        GPIO.output(
            motor["relay"],
            GPIO.HIGH if motor["state"] else GPIO.LOW)
        return motor["state"]

    def emergency_stop(self, channel=None):

        print("!!! EMERGENCY STOP ACTIVATED !!!")

        for motor in self.motors.values():
            motor["state"] = False
            GPIO.output(motor["relay"], GPIO.LOW)

        return self.get_status()
    
    def run_pusher(self, seconds=8):

        def worker():
            with self.lock:
                motor = self.motors["pusher"]
                if motor["state"]:
                    return
                motor["state"] = True
                GPIO.output(motor["relay"], GPIO.HIGH)
            time.sleep(seconds)
            with self.lock:
                motor["state"] = False
                GPIO.output(motor["relay"], GPIO.LOW)

        threading.Thread(target=worker, daemon=True).start()
    
    def get_status(self):

        return {
            name: motor["state"]
            for name, motor in self.motors.items()
        }

    def cleanup(self):
        GPIO.cleanup()


# gpio/controller.py

import RPi.GPIO as GPIO


class MotorController:

    def __init__(self):

        GPIO.setmode(GPIO.BCM)

        # ========================
        # Motor Configuration
        # ========================
        # can add more motors by adding entries here
        self.motors = {
            "main": {"relay": 23, "button": 17, "state": False},
            "bad": {"relay": 24, "button": 27, "state": False},
        }

        self.emergency_button = 22

        # ========================
        # GPIO Setup
        # ========================
        for name, motor in self.motors.items():
            GPIO.setup(motor["relay"], GPIO.OUT)
            GPIO.output(motor["relay"], GPIO.LOW)

            GPIO.setup(motor["button"], GPIO.IN,
                        pull_up_down=GPIO.PUD_DOWN)

            
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
        GPIO.output(motor["relay"], motor["state"])

        print(f"{name.upper()} Motor:", motor["state"])

        return motor["state"]

    def emergency_stop(self, channel=None):

        print("!!! EMERGENCY STOP ACTIVATED !!!")

        for motor in self.motors.values():
            motor["state"] = False
            GPIO.output(motor["relay"], GPIO.LOW)

        return self.get_status()

    def get_status(self):

        return {
            name: motor["state"]
            for name, motor in self.motors.items()
        }

    def cleanup(self):
        GPIO.cleanup()
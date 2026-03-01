# gpio/controller.py

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# ========================
# Pin Configuration
# ========================

button_main = 17
button_bad = 27
button_emergency = 22

relay_main = 23
relay_bad = 24

# ========================
# GPIO Initialization
# ========================

GPIO.setup(button_main, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_bad, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_emergency, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(relay_main, GPIO.OUT)
GPIO.setup(relay_bad, GPIO.OUT)

GPIO.output(relay_main, GPIO.LOW)
GPIO.output(relay_bad, GPIO.LOW)

# ========================
# States
# ========================

main_state = False
bad_state = False

# ========================
# Motor Control Functions
# ========================

def toggle_main(channel=None):
    global main_state
    main_state = not main_state
    GPIO.output(relay_main, main_state)
    print("Main Motor:", main_state)
    return main_state


def toggle_bad(channel=None):
    global bad_state
    bad_state = not bad_state
    GPIO.output(relay_bad, bad_state)
    print("Bad Motor:", bad_state)
    return bad_state


def emergency_stop(channel=None):
    global main_state, bad_state

    print("!!! EMERGENCY STOP ACTIVATED !!!")

    main_state = False
    bad_state = False

    GPIO.output(relay_main, GPIO.LOW)
    GPIO.output(relay_bad, GPIO.LOW)

    return {
        "main_motor": main_state,
        "bad_motor": bad_state
    }


def get_status():
    return {
        "main_motor": main_state,
        "bad_motor": bad_state
    }

# ========================
# Hardware Button Events
# ========================

GPIO.add_event_detect(button_main, GPIO.RISING, callback=toggle_main, bouncetime=300)
GPIO.add_event_detect(button_bad, GPIO.RISING, callback=toggle_bad, bouncetime=300)
GPIO.add_event_detect(button_emergency, GPIO.RISING, callback=emergency_stop, bouncetime=300)
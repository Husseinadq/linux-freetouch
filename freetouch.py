#!/usr/bin/env python3
import evdev
from evdev import UInput, ecodes as e
import sys

# Constants
DEVICE_NAME = "GXTP7863:00 27C6:01E0 Touchpad"
RIGHT_EDGE_X = 3500
LEFT_EDGE_X = 150
Y_SWIPE_THRESHOLD = 50 # Adjust this back to whatever speed you liked!
PALM_THRESHOLD = 8     # Anything larger than this is considered a palm

def get_touchpad():
    """Locates the Huawei Free Touch input device."""
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for dev in devices:
            if dev.name == DEVICE_NAME:
                return dev
    except FileNotFoundError:
        pass
    return None

def tap_key(ui, key_code):
    """Simulates pressing and releasing a media key."""
    ui.write(e.EV_KEY, key_code, 1)
    ui.write(e.EV_KEY, key_code, 0)
    ui.syn()

def main():
    touchpad = get_touchpad()
    
    if not touchpad:
        print(f"Error: Could not find '{DEVICE_NAME}'. Are you running as root?")
        sys.exit(1)

    capabilities = {
        e.EV_KEY: [e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_BRIGHTNESSUP, e.KEY_BRIGHTNESSDOWN]
    }
    
    try:
        ui = UInput(capabilities, name='huawei-freetouch-virtual')
    except evdev.uinput.UInputError as err:
        print(f"UInput error: {err}. Make sure uinput kernel module is loaded.")
        sys.exit(1)

    print(f"Huawei Free Touch Daemon started.")
    print(f"Listening on: {touchpad.path}")

    # State Variables
    is_right_edge = False
    is_left_edge = False
    is_palm = False
    last_y = None

    try:
        for event in touchpad.read_loop():
            # 1. Track Touch Size for Palm Rejection
            if event.type == e.EV_ABS and event.code == e.ABS_MT_TOUCH_MAJOR:
                if event.value >= PALM_THRESHOLD:
                    is_palm = True

            # 2. Track X Coordinate for Edge Detection
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_X:
                is_right_edge = event.value > RIGHT_EDGE_X
                is_left_edge = event.value < LEFT_EDGE_X

            # 3. Track Y Coordinate for Swipe Calculation
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_Y:
                # If a palm is detected, completely ignore the movement
                if is_palm:
                    continue

                current_y = event.value

                if last_y is not None:
                    delta_y = last_y - current_y

                    if abs(delta_y) > Y_SWIPE_THRESHOLD:
                        if is_right_edge:
                            if delta_y > 0:
                                tap_key(ui, e.KEY_VOLUMEUP)
                            else:
                                tap_key(ui, e.KEY_VOLUMEDOWN)
                            last_y = current_y

                        elif is_left_edge:
                            if delta_y > 0:
                                tap_key(ui, e.KEY_BRIGHTNESSUP)
                            else:
                                tap_key(ui, e.KEY_BRIGHTNESSDOWN)
                            last_y = current_y
                else:
                    last_y = current_y

            # 4. Reset State on Touch Release
            elif event.type == e.EV_KEY and event.code == e.BTN_TOUCH:
                if event.value == 0:
                    is_right_edge = False
                    is_left_edge = False
                    is_palm = False # Reset palm status when hand is lifted
                    last_y = None

    except KeyboardInterrupt:
        print("\nDaemon gracefully stopped.")
    finally:
        ui.close()

if __name__ == "__main__":
    main()
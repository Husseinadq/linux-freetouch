#!/usr/bin/env python3
import evdev
import subprocess
import sys

# Constants
DEVICE_NAME = "GXTP7863:00 27C6:01E0 Touchpad"
RIGHT_EDGE_X = 3500
LEFT_EDGE_X = 150
Y_SWIPE_THRESHOLD = 15

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

def execute_command(command):
    """Executes a system shell command safely."""
    try:
        subprocess.run(command, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")

def main():
    touchpad = get_touchpad()
    
    if not touchpad:
        print(f"Error: Could not find '{DEVICE_NAME}'. Are you running as root?")
        sys.exit(1)

    print(f"Huawei Free Touch Daemon started.")
    print(f"Listening on: {touchpad.path}")

    # State Variables
    is_right_edge = False
    is_left_edge = False
    last_y = None

    try:
        for event in touchpad.read_loop():
            # Track X Coordinate for Edge Detection
            if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_MT_POSITION_X:
                is_right_edge = event.value > RIGHT_EDGE_X
                is_left_edge = event.value < LEFT_EDGE_X

            # Track Y Coordinate for Swipe Calculation
            elif event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                current_y = event.value

                if last_y is not None:
                    delta_y = last_y - current_y

                    if abs(delta_y) > Y_SWIPE_THRESHOLD:
                        if is_right_edge:
                            if delta_y > 0:
                                execute_command(["amixer", "-D", "pulse", "sset", "Master", "2%+"])
                            else:
                                execute_command(["amixer", "-D", "pulse", "sset", "Master", "2%-"])
                            last_y = current_y

                        elif is_left_edge:
                            if delta_y > 0:
                                execute_command(["brightnessctl", "set", "2%+"])
                            else:
                                execute_command(["brightnessctl", "set", "2%-"])
                            last_y = current_y
                else:
                    last_y = current_y

            # Reset State on Touch Release
            elif event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_TOUCH:
                if event.value == 0:
                    is_right_edge = False
                    is_left_edge = False
                    last_y = None

    except KeyboardInterrupt:
        print("\nDaemon gracefully stopped.")

if __name__ == "__main__":
    main()

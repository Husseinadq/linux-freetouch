#!/usr/bin/env python3
import evdev
from evdev import UInput, ecodes as e
import sys

# Settings (Percentages instead of hardcoded pixels)
EDGE_WIDTH_PERCENT = 0.05  # The outer 5% of the pad acts as the volume/brightness slider
SWIPE_SENSITIVITY = 0.02   # Finger must travel 2% of the pad's height to trigger 1 tick
PALM_THRESHOLD = 8         # Touch size larger than this is ignored

def get_touchpad():
    """Hunts for any active touchpad on the system."""
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        # Look for common trackpad identifiers in the hardware name
        keywords = ["touchpad", "synaptics", "elan", "alps", "gxtp"]
        
        for dev in devices:
            name_lower = dev.name.lower()
            if any(keyword in name_lower for keyword in keywords):
                # Safely extract the absolute axis codes to check for multi-touch
                caps = dev.capabilities()
                if e.EV_ABS in caps:
                    abs_codes = [cap[0] for cap in caps[e.EV_ABS]]
                    if e.ABS_MT_POSITION_X in abs_codes:
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
        print("Error: Could not find a compatible touchpad. Are you running as root?")
        sys.exit(1)

    # --- DYNAMIC HARDWARE CALIBRATION ---
    caps = dict(touchpad.capabilities()[e.EV_ABS])
    x_info = caps[e.ABS_MT_POSITION_X]
    y_info = caps[e.ABS_MT_POSITION_Y]
    
    min_x, max_x = x_info.min, x_info.max
    min_y, max_y = y_info.min, y_info.max
    
    width = max_x - min_x
    height = max_y - min_y
    
    # Calculate exact edge coordinates based on this specific laptop's hardware
    right_edge_x = max_x - (width * EDGE_WIDTH_PERCENT)
    left_edge_x = min_x + (width * EDGE_WIDTH_PERCENT)
    y_swipe_threshold = height * SWIPE_SENSITIVITY

    print(f"Universal Free Touch Daemon started.")
    print(f"Hooked into: {touchpad.name} ({touchpad.path})")
    print(f"Hardware Resolution: {width}x{height}")
    print(f"Calculated Left Edge: < {left_edge_x} | Right Edge: > {right_edge_x}")

    capabilities = {
        e.EV_KEY: [e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_BRIGHTNESSUP, e.KEY_BRIGHTNESSDOWN]
    }
    
    try:
        ui = UInput(capabilities, name='universal-freetouch-virtual')
    except evdev.uinput.UInputError as err:
        print(f"UInput error: {err}. Make sure uinput kernel module is loaded.")
        sys.exit(1)

    # State Variables
    is_right_edge = False
    is_left_edge = False
    is_palm = False
    last_y = None

    try:
        for event in touchpad.read_loop():
            # 1. Palm Rejection
            if event.type == e.EV_ABS and event.code == e.ABS_MT_TOUCH_MAJOR:
                if event.value >= PALM_THRESHOLD:
                    is_palm = True

            # 2. X Coordinate for Edge Detection
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_X:
                is_right_edge = event.value > right_edge_x
                is_left_edge = event.value < left_edge_x

            # 3. Y Coordinate for Swipe Calculation
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_Y:
                if is_palm:
                    continue

                current_y = event.value

                if last_y is not None:
                    delta_y = last_y - current_y

                    # Use the dynamically calculated threshold!
                    if abs(delta_y) > y_swipe_threshold:
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

            # 4. Reset State
            elif event.type == e.EV_KEY and event.code == e.BTN_TOUCH:
                if event.value == 0:
                    is_right_edge = False
                    is_left_edge = False
                    is_palm = False
                    last_y = None

    except KeyboardInterrupt:
        print("\nDaemon gracefully stopped.")
    finally:
        ui.close()

if __name__ == "__main__":
    main()
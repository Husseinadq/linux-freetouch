#!/usr/bin/env python3
import evdev
from evdev import UInput, ecodes as e
import sys

# --- Settings ---
EDGE_WIDTH_PERCENT = 0.05  # The outer 5% of the pad acts as the volume/brightness slider
TOP_EDGE_PERCENT = 0.05    # The top 5% of the pad acts as the media timeline slider
SWIPE_SENSITIVITY = 0.02   # Finger must travel 2% of the pad's height/width to trigger 1 tick
PALM_THRESHOLD = 8         # Touch size larger than this is ignored

def get_touchpad():
    """Hunts for any active touchpad on the system."""
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        keywords = ["touchpad", "synaptics", "elan", "alps", "gxtp"]
        
        for dev in devices:
            name_lower = dev.name.lower()
            if any(keyword in name_lower for keyword in keywords):
                caps = dev.capabilities()
                if e.EV_ABS in caps:
                    abs_codes = [cap[0] for cap in caps[e.EV_ABS]]
                    if e.ABS_MT_POSITION_X in abs_codes:
                        return dev
    except FileNotFoundError:
        pass
    return None

def tap_key(ui, key_code):
    """Simulates pressing and releasing a key."""
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
    
    # Calculate exact edge boundaries
    right_edge_x = max_x - (width * EDGE_WIDTH_PERCENT)
    left_edge_x = min_x + (width * EDGE_WIDTH_PERCENT)
    top_edge_y = min_y + (height * TOP_EDGE_PERCENT)
    
    y_swipe_threshold = height * SWIPE_SENSITIVITY
    x_swipe_threshold = width * SWIPE_SENSITIVITY

    print(f"Universal Free Touch Daemon started.")
    print(f"Hooked into: {touchpad.name} ({touchpad.path})")
    
    # Add KEY_LEFT and KEY_RIGHT to our virtual keyboard capabilities
    capabilities = {
        e.EV_KEY: [e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN, e.KEY_BRIGHTNESSUP, e.KEY_BRIGHTNESSDOWN, e.KEY_LEFT, e.KEY_RIGHT]
    }
    
    try:
        ui = UInput(capabilities, name='universal-freetouch-virtual')
    except evdev.uinput.UInputError as err:
        print(f"UInput error: {err}. Make sure uinput kernel module is loaded.")
        sys.exit(1)

    # State Variables
    is_right_edge = False
    is_left_edge = False
    is_top_edge = False
    is_palm = False
    last_y = None
    last_x = None

    try:
        for event in touchpad.read_loop():
            # 1. Palm Rejection
            if event.type == e.EV_ABS and event.code == e.ABS_MT_TOUCH_MAJOR:
                if event.value >= PALM_THRESHOLD:
                    is_palm = True

            # 2. X Coordinate Tracking (Detect side edges + Calculate top edge swipe)
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_X:
                is_right_edge = event.value > right_edge_x
                is_left_edge = event.value < left_edge_x

                current_x = event.value
                if not is_palm and is_top_edge:
                    if last_x is not None:
                        delta_x = last_x - current_x
                        if abs(delta_x) > x_swipe_threshold:
                            if delta_x > 0: # Swiped Left (RTL)
                                tap_key(ui, e.KEY_LEFT)
                            else: # Swiped Right (LTR)
                                tap_key(ui, e.KEY_RIGHT)
                            last_x = current_x
                    else:
                        last_x = current_x
                else:
                    last_x = current_x # Keep tracking to prevent jumpy math

            # 3. Y Coordinate Tracking (Detect top edge + Calculate side edge swipes)
            elif event.type == e.EV_ABS and event.code == e.ABS_MT_POSITION_Y:
                is_top_edge = event.value < top_edge_y

                current_y = event.value
                if not is_palm and (is_left_edge or is_right_edge):
                    if last_y is not None:
                        delta_y = last_y - current_y
                        if abs(delta_y) > y_swipe_threshold:
                            if is_right_edge:
                                if delta_y > 0: tap_key(ui, e.KEY_VOLUMEUP)
                                else: tap_key(ui, e.KEY_VOLUMEDOWN)
                            elif is_left_edge:
                                if delta_y > 0: tap_key(ui, e.KEY_BRIGHTNESSUP)
                                else: tap_key(ui, e.KEY_BRIGHTNESSDOWN)
                            last_y = current_y
                    else:
                        last_y = current_y
                else:
                    last_y = current_y

            # 4. Reset State on Touch Release
            elif event.type == e.EV_KEY and event.code == e.BTN_TOUCH:
                if event.value == 0:
                    is_right_edge = False
                    is_left_edge = False
                    is_top_edge = False
                    is_palm = False
                    last_y = None
                    last_x = None

    except KeyboardInterrupt:
        print("\nDaemon gracefully stopped.")
    finally:
        ui.close()

if __name__ == "__main__":
    main()
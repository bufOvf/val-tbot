import json
import numpy as np
from mss import mss
import cv2
import keyboard
import win32api

#TODO: organise keybinds


bot_active = False

def toggle_bot():
    global bot_active
    bot_active = not bot_active
    state = "active" if bot_active else "inactive"
    print(f"Bot is now {state}")

class ScreenCapture:
    def __init__(self, config):
        self.config = config
        self.full_screen_monitor = self.get_full_screen_monitor()
        self.target_monitor = self.get_target_monitor()

    def get_full_screen_monitor(self):
        return {
            "top": 0,
            "left": 0,
            "width": win32api.GetSystemMetrics(0),
            "height": win32api.GetSystemMetrics(1)
        }

    def get_target_monitor(self):
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        box_width = self.config["box_width"]
        box_height = self.config["box_height"]
        left = int((screen_width - box_width) / 2)
        top = int((screen_height - box_height) / 2)
        return left, top, left + box_width, top + box_height

    def capture(self, debug_mode=False):
        monitor = self.full_screen_monitor if debug_mode else {**self.full_screen_monitor, **self.target_monitor} # type: ignore
        with mss() as sct:
            sct_img = sct.grab(monitor)
            return np.array(sct_img)[:, :, :3]

    def color_detected(self, img):
        target_color = np.array(self.config["target_color"])
        tolerance = self.config["color_tolerance"]
        diff = np.abs(img - target_color)
        within_tolerance = np.all(diff <= tolerance, axis=-1)
        return np.any(within_tolerance)

def load_config(config_path="config.json"):
    with open(config_path, "r") as file:
        return json.load(file)

def debug_mode_prompt():
    response = input("debug mode? [Y/n]: ").strip().lower()
    return response != 'n'

def show_capture_with_target_area(img, target_area):

    img_contiguous = np.ascontiguousarray(img) 
    
    window_name = 'Preview'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) 
    
    cv2.rectangle(img_contiguous, (target_area[0], target_area[1]), (target_area[2], target_area[3]), (0, 255, 0), 1)
    cv2.imshow(window_name, img_contiguous)
    cv2.waitKey(1)


def main():
    config = load_config()
    debug_mode = debug_mode_prompt()
    capture = ScreenCapture(config)
    is_shooting = False  
    
    keyboard.add_hotkey('8', toggle_bot) 

    print("Monitoring... Press '9' to exit.")
    try:
        while not keyboard.is_pressed('9'):
            full_img = capture.capture(debug_mode=True)
            target_img = full_img[capture.target_monitor[1]:capture.target_monitor[3], capture.target_monitor[0]:capture.target_monitor[2]]
            target_color_detected = capture.color_detected(target_img)
            

            if target_color_detected and not is_shooting:
                print("Target detected")
                keyboard.press('0')  # Start shooting
                is_shooting = True
            elif not target_color_detected and is_shooting:
                keyboard.release('0')  # Stop shooting
                is_shooting = False
            
            if debug_mode:
                show_capture_with_target_area(full_img, capture.target_monitor)
    except KeyboardInterrupt:
        print("Stopped monitoring.")
    finally:
        keyboard.release('0') 
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
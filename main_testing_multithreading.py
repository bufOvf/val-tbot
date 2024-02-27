import json
import numpy as np
from mss import mss
import keyboard
import win32api
import threading
from threading import Lock

class ScreenCapture:
    def __init__(self, config):
        self.config = config
        self.target_monitor = self.calculate_target_monitor()
        self.latest_capture = None
        self.capture_lock = Lock()

    def calculate_target_monitor(self):
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        box_width = self.config["box_width"]
        box_height = self.config["box_height"]
        left = (screen_width - box_width) // 2
        top = (screen_height - box_height) // 2
        return {
            "top": top,
            "left": left,
            "width": box_width,
            "height": box_height
        }

    def update_capture(self):
        with mss() as sct:
            while bot_active:
                sct_img = sct.grab(self.target_monitor)
                with self.capture_lock:
                    self.latest_capture = np.array(sct_img)[:, :, :3]

    def color_detected(self, img):
        target_color = np.array(self.config["target_color"])
        tolerance = self.config["color_tolerance"]
        
        diff = np.linalg.norm(img - target_color, axis=-1)
        
        return np.any(diff <= tolerance)

def load_config(config_path="config.json"):
    with open(config_path, "r") as file:
        return json.load(file)

def toggle_bot():
    global bot_active
    bot_active = not bot_active
    print(f"Bot is now {'active' if bot_active else 'inactive'}")

def process_images(capture):
    global shooting
    while bot_active:
        img = None
        with capture.capture_lock:
            img = capture.latest_capture
        if img is not None:
            color_detected = capture.color_detected(img)

            if color_detected and not shooting:
                keyboard.press('0')  # Assuming 'k' is bound to shoot
                shooting = True
                print("Shooting started...")
            elif not color_detected and shooting:
                keyboard.release('0')  # Release 'k'
                shooting = False
                print("Shooting stopped...")

bot_active = True
shooting = False  # Track whether we are currently shooting

def main():
    config = load_config()
    capture = ScreenCapture(config)
    keyboard.add_hotkey('5', toggle_bot)

    print("Press 5 to toggle on/off\nPress 9 to exit")

    capture_thread = threading.Thread(target=capture.update_capture, args=())
    processing_thread = threading.Thread(target=process_images, args=(capture,))

    capture_thread.start()
    processing_thread.start()

    try:
        while True:
            if keyboard.is_pressed('9'):  # Exit condition
                global bot_active
                bot_active = False
                break
    except KeyboardInterrupt:
        bot_active = False
        print("Stopped monitoring.")
    finally:
        capture_thread.join()
        processing_thread.join()
        if shooting: 
            keyboard.release('0')
        print("Exiting...")

if __name__ == "__main__":
    main()

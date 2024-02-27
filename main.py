import numpy as np
from mss import mss
import keyboard
import win32api

# Hard-coded configuration
CONFIG = {
  "box_width": 10,
  "box_height": 10,
  "target_color": [250, 100, 250],
  "color_tolerance": 50
}

class ScreenCapture:
    def __init__(self, config):
        self.config = config

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

    def capture(self):
        with mss() as sct:
            sct_img = sct.grab(self.calculate_target_monitor())
            return np.array(sct_img)[:, :, :3]

    def color_detected(self, img):
        target_color = np.array(self.config["target_color"])
        tolerance = self.config["color_tolerance"]
        
        diff = np.linalg.norm(img - target_color, axis=-1)
        
        return np.any(diff <= tolerance)

def toggle_bot():
    global bot_active
    bot_active = not bot_active
    print(f"Bot is now {'active' if bot_active else 'inactive'}")

bot_active = True

def main():
    capture = ScreenCapture(CONFIG)
    keyboard.add_hotkey('5', toggle_bot)

    print("Press 8 to toggle on/off\nPress 9 to exit")

    shooting = False  # Track whether we are currently shooting

    try:
        while True:
            if keyboard.is_pressed('9'):  # Exit condition
                break

            if bot_active:
                img = capture.capture()
                color_detected = capture.color_detected(img)
                
                if color_detected and not shooting:
                    keyboard.press('0')  # Start holding down '0'
                    shooting = True  # Mark as shooting
                    print("Shooting started...")

                elif not color_detected and shooting:
                    keyboard.release('0')  # Stop holding down '0'
                    shooting = False  # Mark as not shooting
                    print("Shooting stopped...")

    except KeyboardInterrupt:
        print("Stopped monitoring.")
    finally:
        if shooting:  # Ensure '0' is released if the script is exiting while shooting
            keyboard.release('0')
        print("Exiting...")

if __name__ == "__main__":
    main()

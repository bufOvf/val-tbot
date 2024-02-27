import numpy as np
from mss import mss
import keyboard
import win32api
import time


# Hard-coded configuration
CONFIG = {
  "box_width": 10,
  "box_height": 3,
  "target_color": [250, 100, 250],
  "color_tolerance": 50
}


class ScreenCapture:
    def __init__(self, config):
        self.config = config
        self.target_monitor = self.calculate_target_monitor() 

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
            sct_img = np.array(sct.grab(self.target_monitor))[:, :, :3]
            return sct_img

        
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

    print("Press 5 to toggle on/off\nPress 9 to exit")

    shooting = False  
    # start_time = time.time() 

    try:
        while True:
            if keyboard.is_pressed('9'): 
                break

            if bot_active:
                img = capture.capture()
                color_detected = capture.color_detected(img)
                
                if color_detected and not shooting:
                    keyboard.press('0')  
                    shooting = True  
                    print("Shoot")

                elif not color_detected and shooting:
                    keyboard.release('0') 
                    shooting = False  
            # mesuring ms delay (idk if this works)
            # if time.time() - start_time >= 10:
            #     print("Script stopped")
            #     break

    except KeyboardInterrupt:
        print("Stopped monitoring.")
    finally:
        if shooting:  
            keyboard.release('0')
        print("Exiting...")

if __name__ == "__main__":
    main()

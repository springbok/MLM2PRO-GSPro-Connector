import ctypes
import math
import cv2
import numpy as np
import win32gui
import win32ui
from PIL import Image
from matplotlib import pyplot as plt
from src.ball_data import BallData
from src.rois import Rois
from src.ui import Color, UI


class Screenshot:

    def __init__(self, settings, app_paths):
        self.rois = Rois(app_paths)
        self.settings = settings
        self.ball_data = BallData()
        self.screenshot = []
        self.new_shot = False
        self.message = None
        self.width = -1
        self.height = -1


    def load_rois(self, reset=False):
        if reset or len(self.rois.values) <= 0:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Saved ROI's not found, please define ROI's from your first shot.")
            self.__get_rois_from_user()
        else:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Using previosuly saved ROI's")

    def __get_rois_from_user(self):
        input("- Press enter after you've hit your first shot. -")
        # Run capture_window function in a separate thread
        self.__capture_screenshot(self.settings.WINDOW_NAME, self.settings.TARGET_WIDTH, self.settings.TARGET_HEIGHT)
        self.rois.rois = []
        # Ask user to select ROIs for each value, if they weren't found in the json
        for value in self.rois.keys:
            print(f"Please select the ROI for {value}.")
            roi = self.__select_roi()
            self.rois.values[value] = roi
        # Save settings file with new settings
        self.rois.write()
        
    def __select_roi(self):
        plt.imshow(cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB))
        plt.show(block=False)
        print("Please select the region of interest (ROI).")
        roi = plt.ginput(n=2)
        plt.close()
        x1, y1 = map(int, roi[0])
        x2, y2 = map(int, roi[1])
        return (x1, y1, x2 - x1, y2 - y1)

    def __capture_screenshot(self, window_name: str, target_width: int, target_height: int):
        ctypes.windll.user32.SetProcessDPIAware()
        hwnd = win32gui.FindWindow(None, window_name)
        if not hwnd:
            raise RuntimeError(f"Can't find window called '{window_name}'")

        rect = win32gui.GetClientRect(hwnd)
        if self.width == -1:
            self.width = rect[2] - rect[0]
            self.height = rect[3] - rect[1]
        else:
            if not (self.width == rect[2] - rect[0] and self.height == rect[3] - rect[0]):
                raise RuntimeError(f"Target window ({window_name}) size has changed to {self.width}x{self.height} {rect}")

        if not (self.width == target_width and self.height == target_height):
            print(f"Dimensions seem wrong {self.width}x{self.height} vs json:{target_width}x{target_height}")

        rect_pos = win32gui.GetWindowRect(hwnd)
        left = rect_pos[0]
        top = rect_pos[1]

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
        save_dc.SelectObject(bitmap)

        result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

        screenshot = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        self.screenshot = np.ascontiguousarray(screenshot)[..., :-1]

        if not result:
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            raise RuntimeError(f"Unable to acquire screenshot! Result: {result}")

    def __recognize_roi(self, roi, api):
        # crop the roi from screenshot
        cropped_img = self.screenshot[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        # use tesseract to recognize the text
        api.SetImage(Image.fromarray(cropped_img))
        result = api.GetUTF8Text()
        cleaned_result = ''.join(c for c in result if c.isdigit() or c == '.' or c == '-' or c == '_' or c == '~')
        return cleaned_result.strip()

    def capture_and_process_screenshot(self, last_shot, api):
        # Check if we have a previous shot
        if last_shot is None:
            diff = True
        else:
            diff = False
        self.__capture_screenshot(self.settings.WINDOW_NAME, self.settings.TARGET_WIDTH, self.settings.TARGET_HEIGHT)
        for key in self.rois.keys:
            # Use ROI to get value from screenshot
            try:
                result = float(self.__recognize_roi(self.rois.values[key], api))
            except Exception as e:
                raise ValueError(f"Could not convert value for '{key}' to float 0")
            # Put the value for the current ROI into the ball data object
            setattr(self.ball_data, self.rois.ball_data_mapping[key], result)
            # Check values are not 0
            if self.rois.ball_data_mapping[key] in self.rois.must_not_be_zero and result == float(0):
                raise ValueError(f"Value for '{key}' is 0")
            # See if values are different from previous shot
            if not diff and not last_shot is None:
                if result != getattr(last_shot, self.rois.ball_data_mapping[key]):
                    diff = True
        if diff:
            self.ball_data.back_spin = round(self.ball_data.total_spin * math.cos(math.radians(self.ball_data.spin_axis)))
            self.ball_data.side_spin = round(self.ball_data.total_spin * math.sin(math.radians(self.ball_data.spin_axis)))

        # Set diff attribute if value are different
        self.new_shot = diff





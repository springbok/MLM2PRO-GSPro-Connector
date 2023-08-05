import ctypes
import logging
import math
import re

import cv2
import numpy as np
import win32gui
import win32ui
from PIL import Image
from matplotlib import pyplot as plt
from src.ball_data import BallData
from src.ui import Color, UI


class Screenshot:

    def __init__(self, settings, app_paths):
        self.settings = settings
        self.ball_data = BallData()
        self.screenshot = []
        self.new_shot = False
        self.message = None
        self.width = -1
        self.height = -1
        self.app_paths = app_paths


    def load_rois(self, reset=False):
        if reset or len(self.settings.rois) <= 0:
            if not reset:
                UI.display_message(Color.GREEN, "CONNECTOR ||", "Saved ROI's not found, please define ROI's from your first shot.")
            self.__get_rois_from_user()
        else:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Using previosuly saved ROI's")

    def __get_rois_from_user(self):
        input("- Press enter after you've hit your first shot. -")
        # Run capture_window function in a separate thread
        self.__capture_screenshot(self.settings.WINDOW_NAME, self.settings.target_width, self.settings.target_height)
        self.settings.rois = []
        # Ask user to select ROIs for each value, if they weren't found in the json
        for key in BallData.properties:
            print(f"Please select the ROI for {BallData.properties[key]}.")
            roi = self.__select_roi()
            self.settings.rois[key] = roi
        # Save settings file with new settings
        self.settings.create()
        
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
        # Need to do more testing on when and how window size changes, for now comment out
        # else:
        #    if not (self.width == rect[2] - rect[0] and self.height == rect[3] - rect[0]):
        #        raise RuntimeError(f"Target window ({window_name}) size has changed to {self.width}x{self.height} {rect}")

        #if not (self.width == target_width and self.height == target_height):
        #    print(f"Dimensions seem wrong {self.width}x{self.height} vs json:{target_width}x{target_height}")

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
        cleaned_result = re.findall(r"[-+]?(?:\d*\.*\d+)", result)[0]
        # Make sure result is an array and has elements
        if type(cleaned_result) in (tuple, list) and len(cleaned_result) > 0:
            cleaned_result = cleaned_result[0]
        return cleaned_result.strip()

    def capture_and_process_screenshot(self, last_shot, api):
        # Check if we have a previous shot
        if last_shot is None:
            diff = True
        else:
            diff = False
        self.__capture_screenshot(self.settings.WINDOW_NAME, self.settings.target_width, self.settings.target_height)
        for key in BallData.properties:
            # Use ROI to get value from screenshot
            try:
                result = self.__recognize_roi(self.settings.rois[key], api)
                #logging.debug(f"key: {key} result: {result}")
                result = float(result)
            except Exception as e:
                raise ValueError(f"Could not convert value for '{BallData.properties[key]}' to float 0")
            # Check values are not 0
            if key in BallData.must_not_be_zero and result == float(0):
                raise ValueError(f"Value for '{BallData.properties[key]}' is 0")
            # For some reason ball speed sometimes get an extra digit added
            if key == 'speed' and result > 400:
                logging.debug(f"Invalid {BallData.properties[key]} value: {result} > 400")
                result = result / 10
            elif key == 'total_spin' and result > 25000:
                logging.debug(f"Invalid {BallData.properties[key]} value: {result} > 25000")
                result = result / 10
            # Put the value for the current ROI into the ball data object
            setattr(self.ball_data, key, result)
            # See if values are different from previous shot
            if not diff and not last_shot is None:
                if result != getattr(last_shot, key):
                    diff = True
        if diff:
            self.ball_data.back_spin = round(self.ball_data.total_spin * math.cos(math.radians(self.ball_data.spin_axis)))
            self.ball_data.side_spin = round(self.ball_data.total_spin * math.sin(math.radians(self.ball_data.spin_axis)))

        # Set diff attribute if value are different
        self.new_shot = diff





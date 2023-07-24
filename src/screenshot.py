import ctypes
import json
import logging
import os
import cv2
import numpy as np
import tesserocr
import win32gui
import win32ui
from PIL import Image
from matplotlib import pyplot as plt

from src.gspro import BallData
from src.rois import Rois
from src.ui import Color, UI


class Screenshot:

    # Use class attribute for OCR as we will only use on instance
    tesserocr_api = None

    @staticmethod
    def initialise_ocr():
        tesseract_path = os.path.join(os.getcwd(), 'Tesseract-OCR')
        tessdata_path = os.path.join(tesseract_path, 'tessdata')
        tesseract_library = os.path.join(tesseract_path, 'libtesseract-5.dll')
        tesserocr.tesseract_cmd = tessdata_path
        ctypes.cdll.LoadLibrary(tesseract_library)
        Screenshot.tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang='train', path=tesserocr.tesseract_cmd)

    def __init__(self, settings, app_paths):
        self.rois = Rois(app_paths)
        self.settings = settings
        self.ball_data = BallData()
        self.screenshot = []
        self.diff = False

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
            logging.info(f"ROI value for {value}: {roi}")
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

        rect = win32gui.GetClientRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]

        rect_pos = win32gui.GetWindowRect(hwnd)
        left = rect_pos[0]
        top = rect_pos[1]

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)

        result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

        self.screenshot = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
        self.screenshot = np.ascontiguousarray(self.screenshot)[..., :-1]

        if not result:
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            raise RuntimeError(f"Unable to acquire screenshot! Result: {result}")

    def __recognize_roi(self, roi):
        # crop the roi from screenshot
        cropped_img = self.screenshot[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        # use tesseract to recognize the text
        Screenshot.tesserocr_api.SetImage(Image.fromarray(cropped_img))
        result = Screenshot.tesserocr_api.GetUTF8Text()
        cleaned_result = ''.join(c for c in result if c.isdigit() or c == '.' or c == '-' or c == '_' or c == '~')
        return cleaned_result.strip()

    def capture_and_process_screenshot(self, previous_shot):
        # Check if we have a previous shot
        previous_shot_object = None
        if len(previous_shot) > 0:
            previous_shot_object = json.loads(previous_shot)
        else:
            diff = True
        self.__capture_screenshot(self.settings.WINDOW_NAME, self.settings.TARGET_WIDTH, self.settings.TARGET_HEIGHT)
        diff = False
        for key in self.rois.keys:
            # Use ROI to get value from screenshot
            result = self.__recognize_roi(self.screenshot, self.rois.values[key])
            # Put the value for the current ROI into the ball data object
            setattr(self.ball_data, self.rois.ball_data_mapping[key], result)
            # Check values are not 0
            if key in self.rois.must_not_be_zero and result <= 0:
                raise ValueError(f"Value for '{key}' is 0")
            # See if values are different from previous shot
            if not diff and not previous_shot_object is None:
                if result != getattr(self.rois.ball_data_mapping[key], previous_shot):
                    diff = True

        # Set diff attribute if value are different
        self.diff = diff





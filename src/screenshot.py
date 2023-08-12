import logging
import math
import re
import cv2
from PIL import Image
from matplotlib import pyplot as plt
from src.application import Application
from src.ball_data import BallData
from src.ctype_screenshot import ScreenMirrorWindow, ScreenshotOfWindow
from src.ui import Color, UI


class Screenshot:

    def __init__(self, application: Application):
        self.application = application
        self.ball_data = BallData()
        self.screenshot = []
        self.new_shot = False
        self.message = None
        self.resize_window = True
        self.mirror_window = None

    def load_rois(self, reset=False):
        if reset or len(self.application.device_manager.current_device.rois) <= 0:
            if not reset:
                UI.display_message(Color.GREEN, "CONNECTOR ||", "Saved ROI's not found, please define ROI's from your first shot.")
            self.__get_rois_from_user()
        else:
            UI.display_message(Color.GREEN, "CONNECTOR ||", "Using previously saved ROI's")

    def __get_rois_from_user(self):
        input("- Press enter after you've hit your first shot and correctly resized the screen mirror window to remove black borders. -")
        # Run capture_window function in a separate thread
        self.__capture_screenshot()
        self.application.device_manager.current_device.rois = {}
        self.application.device_manager.current_device.window_rect = {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}
        # Ask user to select ROIs for each value, if they weren't found in the json
        for key in BallData.rois_properties:
            print(f"Please select the ROI for {BallData.properties[key]}.")
            roi = self.__select_roi()
            self.application.device_manager.current_device.rois[key] = roi
            self.application.device_manager.current_device.save()

    def __select_roi(self):
        plt.imshow(cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB))
        plt.show(block=False)
        print("Please select the region of interest (ROI).")
        roi = plt.ginput(n=2)
        plt.close()
        x1, y1 = map(int, roi[0])
        x2, y2 = map(int, roi[1])
        return (x1, y1, x2 - x1, y2 - y1)

    def __capture_screenshot(self):
        # Find the window using window title
        if self.mirror_window is None:
            self.mirror_window = ScreenMirrorWindow(self.application.device_manager.current_device.window_name)
            self.screenshot_of_window = ScreenshotOfWindow(
                hwnd=self.mirror_window.hwnd,
                client=True,
                ascontiguousarray=True)
        # Resize to correct size if required
        if self.resize_window:
            if self.application.device_manager.current_device.width() <= 0 or self.application.device_manager.current_device.height() <= 0:
                # Obtain current window rect
                self.application.device_manager.current_device.window_rect = {
                    'left': self.mirror_window.rect.left,
                    'top': self.mirror_window.rect.top,
                    'right': self.mirror_window.rect.right,
                    'bottom': self.mirror_window.rect.bottom
                }
                # Write values to settings file
                self.application.device_manager.current_device.save()
                logging.debug(f'No previously saved window dimensions found, saving current window dimentions to config file: {self.application.device_manager.current_device.window_rect}')
            else:
                # Resize window to correct size
                self.mirror_window.resize(
                    self.application.device_manager.current_device.width(),
                    self.application.device_manager.current_device.height())
                logging.debug(f'Loading window dimensions from config file: {self.application.device_manager.current_device.window_rect}')
            self.resize_window = False
        # Take screenshot
        self.screenshot = self.screenshot_of_window.screenshot_window()

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
        self.__capture_screenshot()
        for key in BallData.rois_properties:
            # Use ROI to get value from screenshot
            result = 0
            try:
                result = self.__recognize_roi(self.application.device_manager.current_device.rois[key], api)
                # logging.debug(f"key: {key} result: {result}")
                result = float(result)
            except Exception as e:
                msg = f"Could not convert value {result} for '{BallData.properties[key]}' to float 0"
                # Reset width to -1 to force window to be resized in case that is the cause of the missread
                self.resize_window = True
                logging.debug(msg)
                raise ValueError(msg)
            # Check values are not 0
            if key in BallData.must_not_be_zero and result == float(0):
                raise ValueError(f"Value for '{BallData.properties[key]}' is 0")
            # For some reason ball speed sometimes get an extra digit added
            if key == 'speed' and result > 400:
                logging.debug(f"Invalid {BallData.properties[key]} value: {result} > 400")
                result = result / 10
            elif key == 'total_spin' and result > 20000:
                logging.debug(f"Invalid {BallData.properties[key]} value: {result} > 20000")
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

    def reload_device_settings(self):
        self.resize_window = True
        self.application.device_manager.current_device.load()

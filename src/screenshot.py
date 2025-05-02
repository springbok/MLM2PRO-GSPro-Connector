import logging
from threading import Event

import numpy as np
from PIL import Image

from src.ctype_screenshot import ScreenMirrorWindow, ScreenshotOfWindow
from src.device import Device
from src.screenshot_base import ScreenshotBase
from src.settings import Settings, LaunchMonitor
import tesserocr


class Screenshot(ScreenshotBase):

    def __init__(self, settings: Settings, *args, **kwargs):
        self.settings = settings
        self.device = None
        ScreenshotBase.__init__(self, *args, **kwargs)

    def capture_screenshot(self, device: Device, rois_setup=False):
        # Check if window minimized, for some reason it has a different hwnd when minimized
        # so check here first and restore
        if self.mirror_window and self.mirror_window.is_minimized():
                # Restore the window
                self.mirror_window.restore()
        # Find the window using window title in case a new one was started
        hwnd = ScreenMirrorWindow.find_window(device.window_name)
        if self.mirror_window is None or hwnd != self.mirror_window.hwnd:
            self.mirror_window = ScreenMirrorWindow(device.window_name)
            self.screenshot_image_of_window = ScreenshotOfWindow(
                hwnd=self.mirror_window.hwnd,
                client=True,
                ascontiguousarray=True)
        # Resize to correct size if required
        window_size = self.mirror_window.size()
        if self.resize_window or window_size['h'] != device.height() or window_size['w'] != device.width():
            logging.debug('Resize screen mirror window')
            self.previous_screenshot_image = None
            if device.width() <= 0 or device.height() <= 0:
                # Obtain current window rect
                device.window_rect = {
                    'left': self.mirror_window.rect.left,
                    'top': self.mirror_window.rect.top,
                    'right': self.mirror_window.rect.right,
                    'bottom': self.mirror_window.rect.bottom
                }
                # Write values to settings file
                if not rois_setup:
                    device.save()
                logging.debug(f'No previously saved window dimensions found, saving current window dimentions to config file: {device.window_rect}')
            else:
                # Resize window to correct size
                self.mirror_window.resize(
                    device.width(),
                    device.height())
                # Give window time to resize before taking screenshot
                Event().wait(0.25)
                logging.debug(f'Loading window dimensions from config file: {device.window_rect}')
            self.resize_window = False
        # Take screenshot
        self.screenshot_image = self.screenshot_image_of_window.screenshot_window()
        #im = Image.fromarray(self.screenshot_image)
        #im.save("c:\\python\\test\\screenshot.jpeg")
        # See https://holypython.com/python-pil-tutorial/how-to-convert-an-image-to-black-white-in-python-pil/
        #self.screenshot_image = np.array(Image.open('C:\\python\\android.png').convert('1'))
        #self.screenshot_image = np.array(Image.open('C:\\python\\tesseract_training\\images\\android_1.png'))

        # Check if new shot
        self.new_shot = False
        self.screenshot_new = False
        if self.settings.device_id == LaunchMonitor.UNEEKOR or self.settings.device_id == LaunchMonitor.UNEEKOR_IPAD:
            mse_min = 300
        else: 
            mse_min = 100
        mse = mse_min

        if not self.previous_screenshot_image is None:
            mse = self.mse(self.previous_screenshot_image, self.screenshot_image)
        if mse >= mse_min or self.first:
            self.screenshot_new = True
            self.previous_screenshot_image = self.screenshot_image
            self.image()
            logging.debug(f'Screenshot different mse: {mse}')
        # Check if device changed, if so update roi's
        if self.device != device:
            self.device = device
            self.update_rois(device.rois)
        # To reset roi values pass in device without rois
        if rois_setup and len(device.rois) <= 0:
            self.update_rois(device.rois)

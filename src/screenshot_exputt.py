import logging
from threading import Event
import tesserocr
from src.ctype_screenshot import ScreenMirrorWindow, ScreenshotOfWindow
from src.custom_exception import CameraWindowNotFoundException
from src.screenshot_base import ScreenshotBase
from src.tesserocr_cvimage import TesserocrCVImage


class ScreenshotExPutt(ScreenshotBase):

    def __init__(self, *args, **kwargs):
        ScreenshotBase.__init__(self, *args, **kwargs)
        self.tesserocr_api = TesserocrCVImage(psm=tesserocr.PSM.SINGLE_LINE, lang='exputt', path='.\\')
        

    def capture_screenshot(self, settings, rois_setup=False):
        # Find the window using window title in case a new one was started
        try:
            self.mirror_window = ScreenMirrorWindow(settings.exputt['window_name'])
        except Exception as e:
            raise CameraWindowNotFoundException(format(e))
        # Check if window minimized, for some reason it has a different hwnd when minimized
        # so check here first and restore
        if self.mirror_window.is_minimized():
                # Restore the window
                self.mirror_window.restore()
        self.screenshot_image_of_window = ScreenshotOfWindow(
            hwnd=self.mirror_window.hwnd,
            client=True,
            ascontiguousarray=True)
        # Resize to correct size if required
        window_size = self.mirror_window.size()
        if self.resize_window or window_size['h'] != settings.height() or window_size['w'] != settings.width():
            logging.debug('Resize screen mirror window')
            self.previous_screenshot_image = None
            if settings.width() <= 0 or settings.height() <= 0:
                # Obtain current window rect
                settings.exputt['window_rect'] = {
                    'left': self.mirror_window.rect.left,
                    'top': self.mirror_window.rect.top,
                    'right': self.mirror_window.rect.right,
                    'bottom': self.mirror_window.rect.bottom
                }
                # Write values to settings file
                if not rois_setup:
                    settings.save()
                logging.debug(f'No previously saved window dimensions found, saving current window dimentions to config file: {settings.exputt["window_rect"]}')
            else:
                # Resize window to correct size
                self.mirror_window.resize(
                    settings.width(),
                    settings.height())
                # Give window time to resize before taking screenshot
                Event().wait(0.25)
                logging.debug(f'Loading window dimensions from config file: {settings.exputt["window_rect"]}')
            self.resize_window = False
        # Take screenshot
        self.screenshot_image = self.screenshot_image_of_window.screenshot_window()
        #im = Image.fromarray(self.screenshot_image)
        #im.save("c:\\python\\test\\putt.jpeg")

        # Check if new shot
        self.new_shot = False
        self.screenshot_new = False
        mse = 1
        if not self.previous_screenshot_image is None:
            mse = self.mse(self.previous_screenshot_image, self.screenshot_image)
        if mse > 0.05:
            self.screenshot_new = True
            self.previous_screenshot_image = self.screenshot_image
            self.image()
            logging.debug(f'Screenshot different mse: {mse}')
        # To reset roi values pass in device without rois
        if rois_setup or len(settings.exputt['rois']) <= 0:
            self.update_rois(settings.exputt['rois'])

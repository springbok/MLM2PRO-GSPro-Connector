import logging
import math
import re
from threading import Event
import numpy as np
import pyqtgraph as pg
import tesserocr
from PIL import Image
from pyqtgraph import ViewBox
from src.ball_data import BallData
from src.ctype_screenshot import ScreenMirrorWindow, ScreenshotOfWindow
from src.device import Device
from src.labeled_roi import LabeledROI
from src.tesserocr_cvimage import TesserocrCVImage


class Screenshot(ViewBox):

    roi_color = "blue"
    roi_pen_width = 2
    roi_size_factor = 0.2

    def __init__(self, *args, **kwargs):
        ViewBox.__init__(self, *args, **kwargs)
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.resize_window = True
        self.image_width = 0
        self.image_height = 0
        self.image_rois = {}
        self.device = None
        self.previous_screenshot_image = None
        self.screenshot_image = []
        self.mirror_window = None
        self.screenshot_image_of_window = None
        self.new_shot = False
        self.screenshot_new = False
        self.previous_balldata = None
        self.balldata = None
        self.__setupUi()
        self.tesserocr_api = TesserocrCVImage(psm=tesserocr.PSM.SINGLE_WORD, lang='train')
        self.setAspectLocked(True)
        self.setMenuEnabled(False)
        self.invertY(True)

    def __setupUi(self):
        self.image_item = pg.ImageItem(None)
        self.addItem(self.image_item)
        self.__create_rois()

    def __image(self):
        self.image_item.setImage(self.screenshot_image)
        #self.setLimits(xMin=0, xMax=self.image_item.width(), yMin=0, yMax=self.image_item.height())
        self.setRange(xRange=[0, self.image_item.width()], yRange=[0, self.image_item.height()])
        self.image_width = self.image_item.width()
        self.image_height = self.image_item.height()

    def update_rois(self, rois):
        if len(self.image_rois) > 0 and len(rois) > 0:
            for roi in BallData.rois_properties:
                if roi in rois and len(rois[roi]) > 0:
                    self.image_rois[roi].setState(rois[roi])
        else:
            self.__self_reset_rois()

    def __create_rois(self):
        if len(self.image_rois) <= 0:
            for roi in BallData.rois_properties:
                self.image_rois[roi] = LabeledROI(
                    [0, 0], [self.image_width * Screenshot.roi_size_factor, self.image_height * Screenshot.roi_size_factor],
                    pen=({'color': Screenshot.roi_color, 'width': Screenshot.roi_pen_width}),
                    label=BallData.properties[roi])
                self.addItem(self.image_rois[roi])

    def __self_reset_rois(self):
        rois = {}
        for roi in BallData.rois_properties:
            rois[roi] = {
                "pos": [0, 0],
                "size": [self.image_width * Screenshot.roi_size_factor, self.image_height * Screenshot.roi_size_factor],
                "angle": 0
            }
        self.update_rois(rois)

    def get_rois(self):
        rois = {}
        if not self.image_rois is None:
            for roi in self.image_rois:
                rois[roi] = self.image_rois[roi].saveState()
        return rois

    def zoom(self, in_or_out):
        """
        see ViewBox.scaleBy()
        pyqtgraph wheel zoom is s = ~0.75
        """
        s = 0.9
        zoom = (s, s) if in_or_out == "in" else (1 / s, 1 / s)
        self.scaleBy(zoom)

    def ocr_image(self):
        self.balldata = BallData()
        self.new_shot = False
        for roi in BallData.rois_properties:
            cropped_img = self.image_rois[roi].getArrayRegion(self.screenshot_image, self.image_item)
            img = np.uint8(cropped_img)
            self.tesserocr_api.SetCVImage(img)
            ocr_result = self.tesserocr_api.GetUTF8Text()
            msg = None
            result = ''
            try:
                cleaned_result = re.findall(r"[-+]?(?:\d*\.*\d+)", ocr_result)
                if isinstance(cleaned_result, list or tuple) and len(cleaned_result) > 0:
                    cleaned_result = cleaned_result[0]
                cleaned_result = cleaned_result.strip()
                result = float(cleaned_result)
                # Check values are not 0
                if roi in BallData.must_not_be_zero and result == float(0):
                    raise ValueError(f"Value for '{BallData.properties[roi]}' is 0")
                # For some reason ball speed sometimes get an extra digit added
                if roi == 'speed' and result > 400:
                    logging.debug(f"Invalid {BallData.properties[roi]} value: {result} > 400")
                    result = result / 10
                elif roi == 'total_spin' and result > 15000:
                    logging.debug(f"Invalid {BallData.properties[roi]} value: {result} > 15000")
                    result = result / 10
                setattr(self.balldata, roi, result)
                # Check previous ball data if required
                if not self.new_shot and not self.previous_balldata is None:
                    previous_metric = getattr(self.previous_balldata, roi)
                    if int(previous_metric) != int(result):
                        self.new_shot = True
            except ValueError as e:
                msg = f'{format(e)}'
            except:
                msg = f"Could not convert value {result} for '{BallData.properties[roi]}' to float 0"
            finally:
                if not msg is None:
                    # Force resize
                    self.resize_window = True
                    logging.debug(msg)
                    self.balldata.errors[roi] = msg
                    setattr(self.balldata, roi, BallData.invalid_value)
                else:
                    self.balldata.back_spin = round(
                        self.balldata.total_spin * math.cos(math.radians(self.balldata.spin_axis)))
                    self.balldata.side_spin = round(
                        self.balldata.total_spin * math.sin(math.radians(self.balldata.spin_axis)))
        if self.new_shot or self.previous_balldata is None:
            if len(self.balldata.errors) > 0:
                self.balldata.good_shot = False
            else:
                self.balldata.good_shot = True
            self.previous_balldata = self.balldata.__copy__()

    def capture_screenshot(self, device: Device, rois_setup=False):
        # Find the window using window title
        hwnd = ScreenMirrorWindow.find_window(device.window_name)
        if self.mirror_window is None or hwnd != self.mirror_window.hwnd:
            self.mirror_window = ScreenMirrorWindow(device.window_name)
            self.screenshot_image_of_window = ScreenshotOfWindow(
                hwnd=self.mirror_window.hwnd,
                client=True,
                ascontiguousarray=True)
        # Make sure window is not minimized
        if self.mirror_window.is_minimized():
            self.mirror_window.restore()
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
        #self.screenshot_image = np.array(Image.open('C:\python\mlm2pro-gspro-connect-gui\screenshot1.png'))

        # Check if new shot
        self.new_shot = False
        self.screenshot_new = False
        mse = 1
        if not self.previous_screenshot_image is None:
            mse = self.__mse(self.previous_screenshot_image, self.screenshot_image)
        if mse > 0.05:
            self.screenshot_new = True
            self.previous_screenshot_image = self.screenshot_image
            self.__image()
            logging.debug(f'Screenshot different mse: {mse}')
        # Check if device changed, if so update roi's
        if self.device != device:
            self.device = device
            self.update_rois(device.rois)
        # To reset roi values pass in device without rois
        if rois_setup and len(device.rois) <= 0:
            self.update_rois(device.rois)

    def __mse(self, imageA, imageB):
        err = 0
        try:
            # the 'Mean Squared Error' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            err /= float(imageA.shape[0] * imageA.shape[1])
        except:
            # If error force new screenshot
            err = 10
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err

    def shutdown(self):
        self.tesserocr_api.End()

    @staticmethod
    def screen_mirror_app_running(device):
        return ScreenMirrorWindow.find_window(device.window_name)


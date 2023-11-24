import logging
import os
import time
import numpy as np
import pyqtgraph as pg
import tesserocr
from PIL import Image
from pyqtgraph import ViewBox
from src.ball_data import BallData
from src.labeled_roi import LabeledROI
from src.settings import LaunchMonitor


class ScreenshotBase(ViewBox):

    roi_color = "blue"
    roi_pen_width = 2
    roi_size_factor = 0.2

    def __init__(self, *args, **kwargs):
        ViewBox.__init__(self, *args, **kwargs)
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.resize_window = False
        self.screenshot_new = False
        self.image_rois = {}
        self.image_width = 0
        self.image_height = 0
        self.first = True
        self.mirror_window = None
        self.screenshot_image = np.empty([2, 2])
        self.screenshot_image_of_window = None
        self.previous_screenshot_image = None
        self.new_shot = False
        self.previous_balldata = None
        self.previous_balldata_error = None
        self.balldata = None
        self.__setupUi()
        self.setAspectLocked(True)
        self.setMenuEnabled(False)
        self.invertY(True)

    def __setupUi(self):
        self.image_item = pg.ImageItem(None)
        self.addItem(self.image_item)
        self.__create_rois()

    def image(self):
        self.image_item.setImage(self.screenshot_image)
        #self.setLimits(xMin=0, xMax=self.image_item.width(), yMin=0, yMax=self.image_item.height())
        self.setRange(xRange=[0, self.image_item.width()], yRange=[0, self.image_item.height()])
        self.image_width = self.image_item.width()
        self.image_height = self.image_item.height()

    def update_rois(self, rois):
        if len(self.image_rois) > 0 and len(rois) > 0:
            for roi in self.rois_properties():
                if roi in rois and len(rois[roi]) > 0:
                    self.image_rois[roi].setState(rois[roi])
        else:
            self.__self_reset_rois()

    def rois_properties(self):
        rois_properties = BallData.rois_properties
        logging.debug(f"self.__class__.__name__: {self.__class__.__name__}")
        if self.__class__.__name__ == 'ScreenshotExPutt':
            logging.debug(f'ScreenshotExPutt')
            rois_properties = BallData.rois_putting_properties
        return rois_properties

    def __create_rois(self):
        if len(self.image_rois) <= 0:
            for roi in self.rois_properties():
                self.image_rois[roi] = LabeledROI(
                    [0, 0], [self.image_width * ScreenshotBase.roi_size_factor, self.image_height * ScreenshotBase.roi_size_factor],
                    pen=({'color': ScreenshotBase.roi_color, 'width': ScreenshotBase.roi_pen_width}),
                    label=BallData.properties[roi])
                self.addItem(self.image_rois[roi])

    def __self_reset_rois(self):
        rois = {}
        for roi in self.rois_properties():
            rois[roi] = {
                "pos": [0, 0],
                "size": [self.image_width * ScreenshotBase.roi_size_factor, self.image_height * ScreenshotBase.roi_size_factor],
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

    def mse(self, imageA, imageB):
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

    def ocr_image(self):
        self.balldata = BallData()
        self.new_shot = False
        if self.__class__.__name__ == 'ScreenshotExPutt':
            train_file = 'exputt'
        else:
            train_file = 'train'
            if self.settings.device_id == LaunchMonitor.MEVOPLUS:
                train_file = 'mevo'
        logging.debug(f"Using {train_file}_traineddata for OCR")
        tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang=train_file, path='.\\')
        try:
            for roi in self.rois_properties():
                cropped_img = self.image_rois[roi].getArrayRegion(self.screenshot_image, self.image_item)
                img = Image.fromarray(np.uint8(cropped_img))
                if self.__class__.__name__ != 'ScreenshotExPutt' and self.settings.device_id == LaunchMonitor.MLM2PRO:
                    # Convert to black text on white background, remove background
                    threshold = 180
                    img = img.point(lambda x: 0 if x > threshold else 255)
                #filename = time.strftime(f"{roi}.bmp")
                #path = f"{os.getcwd()}\\appdata\\logs\\{filename}"
                #img.save(path)
                tesserocr_api.SetImage(img)
                ocr_result = tesserocr_api.GetUTF8Text()
                logging.debug(f'ocr {roi}: {ocr_result}')
                if self.__class__.__name__ == 'ScreenshotExPutt':
                    self.balldata.process_putt_data(ocr_result, roi, self.previous_balldata)
                else:
                    self.balldata.process_shot_data(ocr_result, roi, self.previous_balldata, self.settings.device_id)
            # Correct metrics if invalid smash factor
            #if self.balldata.putt_type is None:
            #    self.balldata.check_smash_factor()
            self.new_shot = self.balldata.new_shot
            if self.new_shot:
                if len(self.balldata.errors) > 0:
                    self.balldata.good_shot = False
                    if not self.previous_balldata_error is None and self.balldata.eq(self.previous_balldata_error) <= 0:
                        # Duplicate error ignore
                        self.new_shot = False
                    else:
                        # New error
                        self.previous_balldata_error = self.balldata.__copy__()
                        self.resize_window = True
                    logging.debug('Errors found in shot data')
                    #filename = time.strftime("%Y%m%d-%H%M%S.jpeg")
                    #path = f"{os.getcwd()}\\appdata\\logs\\{filename}"
                    #im = Image.fromarray(self.screenshot_image)
                    #im.save(path)
                else:
                    if not self.previous_balldata is None and self.balldata.eq(self.previous_balldata) <= 1:
                        # If there is only 1 metric different then it's likely this is not a new shot
                        # for example if rapsodo times out or someone changes clubs on the rapsodo
                        self.new_shot = False
                        logging.debug('Only 1 metric different from previous shot, probably not a new shot, ignoring')
                    else:
                        # Good shot
                        logging.debug(f'New valid shot, data: {self.balldata.to_json()}')
                        self.balldata.good_shot = True
                        self.previous_balldata = self.balldata.__copy__()
            else:
                logging.debug('Not a new shot')
            # Ignore first shot at startup
            if self.first:
                logging.debug('First shot, ignoring')
                self.first = False
                self.balldata.new_shot = False
                self.new_shot = False
        finally:
            tesserocr_api.End()


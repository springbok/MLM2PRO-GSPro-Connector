import logging
import os
import cv2
import numpy as np
import pyqtgraph as pg
import tesserocr
from PIL import Image, ImageOps
from pyqtgraph import ViewBox
from src.ball_data import BallData, BallMetrics
from src.labeled_roi import LabeledROI
from src.settings import LaunchMonitor


class ScreenshotBase(ViewBox):

    roi_color = "blue"
    roi_pen_width = 2
    roi_size_factor = 0.2

    def __init__(self, *args, **kwargs):
        ViewBox.__init__(self, *args, **kwargs)
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.selected_club = None
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
        logging.debug(f"self.__class__.__name__: {self.__class__.__name__}")
        if self.__class__.__name__ == 'ScreenshotExPutt':
            logging.debug(f'ScreenshotExPutt')
            rois_properties = BallData.rois_putting_properties
            BallData.properties[BallMetrics.HLA] = "Launch Dir"
            BallData.properties[BallMetrics.CLUB_PATH] = "Putter path"
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = "Impact Angle"
        elif self.settings.device_id == LaunchMonitor.UNEEKOR or self.settings.device_id == LaunchMonitor.UNEEKOR_IPAD :
            rois_properties = BallData.rois_uneekor_properties
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.HLA] = "Side Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Attack Angle"
        elif self.settings.device_id ==  LaunchMonitor.MEVOPLUS :
            rois_properties = BallData.rois_mevoplus_properties
            BallData.properties[BallMetrics.VLA] = "Launch V"
            BallData.properties[BallMetrics.HLA] = "Launch H"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = 'AOA'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Face to target'
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to path'
        elif self.settings.device_id ==  LaunchMonitor.R50:
            rois_properties = BallData.rois_r50_properties
            BallData.properties[BallMetrics.HLA] = "Launch Direction"
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = "Club path"
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Attack Angle"
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to Path'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Club Face'
        elif self.settings.device_id ==  LaunchMonitor.SKYTRAKPLUS :
            rois_properties = BallData.rois_skytrak_properties
            BallData.properties[BallMetrics.VLA] = "Launch Angle"
            BallData.properties[BallMetrics.HLA] = "Side Angle"
            BallData.properties[BallMetrics.CLUB_PATH] = 'Club path'
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Face to target'
            BallData.properties[BallMetrics.CLUB_FACE_TO_PATH] = 'Face to path'
        else : # defaults
            rois_properties = BallData.rois_properties
            BallData.properties[BallMetrics.HLA] = "Launch Direction (HLA)"
            BallData.properties[BallMetrics.VLA] = "Launch Angle (VLA)"
            BallData.properties[BallMetrics.CLUB_PATH] = 'Club path'
            BallData.properties[BallMetrics.ANGLE_OF_ATTACK] = "Angle of Attack"
            BallData.properties[BallMetrics.CLUB_FACE_TO_TARGET] = 'Impact Angle'
        
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
        self.balldata.club = self.selected_club
        self.new_shot = False
        fallback_tesserocr_api = None
        if self.__class__.__name__ == 'ScreenshotExPutt':
            train_file = 'exputt'
        else:
            self.balldata.launch_monitor = self.settings.device_id
            train_file = 'train'
            if self.settings.device_id == LaunchMonitor.MEVOPLUS:
                train_file = 'mevo'
            elif self.settings.device_id == LaunchMonitor.FSKIT:
                train_file = 'fskit'
            elif self.settings.device_id == LaunchMonitor.R50:
                train_file = 'r50'
            elif self.settings.device_id == LaunchMonitor.TRACKMAN:
                train_file = 'trackman'
            elif self.settings.device_id == LaunchMonitor.TRUGOLF_APOGEE:
                train_file = 'apex'
            elif self.settings.device_id == LaunchMonitor.UNEEKOR:
                train_file = 'uneekor'
            elif self.settings.device_id == LaunchMonitor.UNEEKOR_IPAD:
                train_file = 'uneekor_ipad'
            elif self.settings.device_id == LaunchMonitor.SKYTRAKPLUS:
                train_file = 'skytrak'
            elif self.settings.device_id == LaunchMonitor.XSWINGPRO:
                train_file = 'xswingpro'
            elif self.settings.device_id == LaunchMonitor.SQUARE:
                train_file = 'square'
            elif self.settings.device_id == LaunchMonitor.SC4:
                train_file = 'voicecaddiesc4'

        logging.debug(f"Using {train_file}.traineddata for OCR")
        tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_WORD, lang=train_file, path='.\\')
        try:
            pil_img = Image.fromarray(self.screenshot_image).convert('RGB')
            sc = np.array(pil_img)
            for roi in self.rois_properties():
                cropped_img = self.image_rois[roi].getArrayRegion(sc, self.image_item)
                if self.__class__.__name__ != 'ScreenshotExPutt' and self.settings.device_id == LaunchMonitor.MLM2PRO and self.settings.zoom_images == "Yes":
                    logging.debug(f'ocr {roi} - zoom image')
                    original_height, original_width = cropped_img.shape[:2]
                    #print(f"width: {original_width} height: {original_height}")
                    cropped_img = cv2.resize(cropped_img,
                                               (int(original_height * 6), int(original_width * 2)),
                                               interpolation=cv2.INTER_LINEAR)
                # Create PIL image and convert to grey scale
                img = Image.fromarray(np.uint8(cropped_img)).convert('L')
                #width, height = img.size
                #img = img.resize(int(width * factor), int(height * factor))
                if self.__class__.__name__ != 'ScreenshotExPutt' and self.settings.device_id == LaunchMonitor.MLM2PRO:
                    # Convert to black text on white background, remove background
                    threshold = self.settings.colour_threshold
                    logging.debug(f'ocr {roi} - using threshold: {threshold}')
                    img = img.point(lambda x: 0 if x > threshold else 255)
                    #filename = time.strftime(f"{roi}_%Y%m%d-%H%M%S.bmp")
                    #filename = time.strftime(f"{roi}.bmp")
                    #path = f"{os.getcwd()}\\appdata\\logs\\original_{filename}"
                    #img.save(path)
                    bbox = ImageOps.invert(img).getbbox()
                    bbox = img.point(lambda x: 255 - x).getbbox()
                    logging.debug(f'ocr {roi} - bounding box for white space removal: {bbox}')
                    bbox1 = []
                    if bbox is not None:
                        for i in range(len(bbox)):
                            if (i == 0 or i == 1) and bbox[i] > 0: # left & upper
                                new_value = bbox[i] - 5
                                if new_value > 0:
                                    bbox1.append(new_value)
                                else:
                                    bbox1.append(0)
                            elif (i == 2 or i == 3): # right & lower
                                bbox1.append(bbox[i] + 5)
                            else:
                                bbox1.append(bbox[i])
                        logging.debug(f'ocr {roi} - modified bounding box with a small amount of white space added: {bbox1}')
                        img = img.crop(bbox1)
                    if self.settings.create_debug_images == 'Yes':
                        filename = f"{roi}.bmp"
                        path = f"{os.getcwd()}\\appdata\\logs\\{filename}"
                        img.save(path)
                tesserocr_api.SetImage(img)
                ocr_result = tesserocr_api.GetUTF8Text()
                conf = tesserocr_api.MeanTextConf()
                logging.debug(f'ocr {roi} - confidence: {conf} result: {ocr_result.strip()}')
                if conf <= 0:
                    logging.debug(f'ocr {roi} confidence <= 0 retrying with RAW_LINE')
                    if fallback_tesserocr_api is None:
                        fallback_tesserocr_api = tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.RAW_LINE, lang=train_file, path='.\\')
                    fallback_tesserocr_api.SetImage(img)
                    ocr_result = fallback_tesserocr_api.GetUTF8Text()
                    conf = fallback_tesserocr_api.MeanTextConf()
                    logging.debug(f'fallback ocr {roi} - confidence: {conf} result: {ocr_result}')
                if self.__class__.__name__ == 'ScreenshotExPutt':
                    self.balldata.process_putt_data(ocr_result, roi, self.previous_balldata)
                else:
                    self.balldata.process_shot_data(ocr_result, roi, self.previous_balldata, self.selected_club, self.settings.mevo_plus['offline_mode'])

            # Correct metrics if invalid smash factor
            if self.balldata.putt_type is None:
                self.balldata.check_smash_factor(self.selected_club)

            # Ignore first shot at startup
            if self.first:
                logging.debug('First shot, ignoring')
                self.first = False
                self.previous_balldata = self.balldata.__copy__()

            if not self.previous_balldata is None:
                diff_count = self.balldata.eq(self.previous_balldata)
            else:
                diff_count = 1
            self.new_shot = diff_count > 0
            if self.new_shot:
                if len(self.balldata.errors) > 0:
                    self.balldata.good_shot = False
                    if not self.previous_balldata_error is None and self.balldata.eq(self.previous_balldata_error) <= 1:
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
                    if self.balldata.putt_type is None and not self.previous_balldata is None and diff_count <= 1:
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
        finally:
            tesserocr_api.End()


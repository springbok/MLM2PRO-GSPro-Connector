import json
import logging
import math
import re
from dataclasses import dataclass

from src.settings import LaunchMonitor


@dataclass
class PuttType:
    WEBCAM = 'webcam'
    EXPUTT = 'exputt'

@dataclass
class BallColor:
    WHITE = "white"
    WHITE2 = "white2"
    YELLOW = "yellow"
    YELLOW2 = "yellow2"
    ORANGE = "orange"
    ORANGE2 = "orange2"
    ORANGE3 = "orange3"
    ORANGE4 = "orange4"
    GREEN = "green"
    GREEN2 = "green2"
    RED = "red"
    RED2 = "red2"


@dataclass
class BallMetrics:
    SPEED = 'speed'
    SPIN_AXIS = 'spin_axis'
    TOTAL_SPIN = 'total_spin'
    HLA = 'hla'
    VLA = 'vla'
    CLUB_SPEED = 'club_speed'
    BACK_SPIN = 'back_spin'
    SIDE_SPIN = 'side_spin'
    CLUB_PATH = 'path'
    CLUB_FACE_TO_TARGET = 'face_to_target'


class BallData:
    invalid_value = 9999999
    properties = {
        BallMetrics.SPEED: 'Ball Speed',
        BallMetrics.SPIN_AXIS: 'Spin Axis',
        BallMetrics.TOTAL_SPIN: 'Spin Rate',
        BallMetrics.HLA: 'Launch Direction (HLA)',
        BallMetrics.VLA: 'Launch Angle (VLA)',
        BallMetrics.CLUB_SPEED: 'Club Speed',
        BallMetrics.BACK_SPIN: 'Back Spin',
        BallMetrics.SIDE_SPIN: 'Side Spin',
        BallMetrics.CLUB_PATH: 'Club Path',
        BallMetrics.CLUB_FACE_TO_TARGET: 'Impact Angle'
    }
    rois_properties = [BallMetrics.SPEED,
                       BallMetrics.TOTAL_SPIN,
                       BallMetrics.SPIN_AXIS,
                       BallMetrics.HLA,
                       BallMetrics.VLA,
                       BallMetrics.CLUB_SPEED]
    rois_putting_properties = [
        BallMetrics.SPEED,
        BallMetrics.HLA,
        BallMetrics.CLUB_PATH,
        BallMetrics.CLUB_FACE_TO_TARGET
    ]
    must_not_be_zero = [BallMetrics.SPEED,
                        BallMetrics.TOTAL_SPIN,
                        BallMetrics.CLUB_SPEED]
    must_not_be_zero_putt = [BallMetrics.SPEED]

    def __init__(self, *initial_data, **kwargs):
        self.putt_type = None
        self.good_shot = False
        self.new_shot = False
        self.corrections = {}
        self.errors = {}
        for key in BallData.properties:
            setattr(self, key, 0)
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __copy__(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: dict((key, value) for key, value in o.__dict__.items() if key != 'errors' and key != 'good_shot'))

    @staticmethod
    def ballcolor_as_list():
        keys = []
        for key in BallColor.__dict__:
            if key != '__' not in key:
                keys.append(getattr(BallColor, key))
        return keys

    def to_gspro(self):
        payload = {
            "BallData": {
                "Speed": self.speed,
                "SpinAxis": self.spin_axis,
                "TotalSpin": self.total_spin,
                "HLA": self.hla,
                "VLA": self.vla,
                "Backspin": self.back_spin,
                "SideSpin": self.side_spin
            },
            "ClubData": {
                "Speed": self.club_speed
            },
            "ShotDataOptions": {
                "ContainsBallData": True,
                "ContainsClubData": True,
                "LaunchMonitorIsReady": True,
                "LaunchMonitorBallDetected": True,
                "IsHeartBeat": False
            }
        }
        if not self.putt_type is None and self.putt_type == PuttType.EXPUTT:
            payload['ClubData']['Path'] = self.path
            payload['ClubData']['FaceToTarget'] = self.face_to_target
        return payload

    def from_gspro(self, payload):
        self.speed = payload['BallData']['Speed']
        self.spin_axis = payload['BallData']['SpinAxis']
        self.total_spin = payload['BallData']['TotalSpin']
        self.hla = payload['BallData']['HLA']
        self.vla = payload['BallData']['VLA']
        self.back_spin = payload['BallData']['Backspin']
        self.side_spin = payload['BallData']['SideSpin']
        self.club_speed = payload['ClubData']['Speed']
        if 'Path' in payload['ClubData']:
            self.path = payload['ClubData']['Path']
            self.face_to_target = payload['ClubData']['FaceToTarget']

    def process_putt_data(self, ocr_result, roi, previous_balldata):
        self.putt_type = PuttType.EXPUTT
        msg = None
        result = ''
        try:
            # Strip non ascii chars
            ocr_result = re.sub(r'[^\x00-\x7f]',r'', ocr_result)
            logging.debug(f'remove non ASCII {roi}: {ocr_result}')
            cleaned_result = re.findall(r"[LR]?(?:\d*\.*\d)", ocr_result)
            logging.debug(f'cleaned_result {roi}: {cleaned_result}')
            if isinstance(cleaned_result, list or tuple) and len(cleaned_result) > 0:
                cleaned_result = cleaned_result[0]
            logging.debug(f'cleaned_result {roi}: {cleaned_result}')
            if len(cleaned_result) > 0:
                cleaned_result = cleaned_result.strip()
            if len(cleaned_result) <= 0:
                logging.debug(f"Value for {BallData.properties[roi]} is empty")
                cleaned_result = '0'
            # Remove any leading '.' sometimes a - is read as a '.'
            logging.debug(f'cleaned result {roi}: {cleaned_result}')
            result = cleaned_result.lstrip('.')
            logging.debug(f'result {roi}: {result}')
            # Check values are not 0
            if roi == BallMetrics.SPEED:
                result = float(result)
            if roi == BallMetrics.HLA:
                if result[0] == 'L':
                    result = -float(result[1:])
                else:
                    result = float(result[1:])
            if roi == BallMetrics.CLUB_PATH and result != '0':
                if result[0] == 'L':
                    # left, negative for GSPRO
                    result = -float(result[1:])
                else:
                    result = float(result[1:])
            if roi == BallMetrics.CLUB_FACE_TO_TARGET and result != '0':
                if result[0] == 'L':
                    # left, negative for GSPRO
                    result = -float(result[1:])
                else:
                    result = float(result[1:])
            if roi in BallData.must_not_be_zero_putt and result == float(0):
                raise ValueError(f"Value for '{BallData.properties[roi]}' is 0")
            if roi == BallMetrics.SPEED:
                if result > 40:
                    result = self.__fix_out_of_bounds_metric(40, result, roi)
                    self.corrections[roi] = True
                setattr(self, BallMetrics.CLUB_SPEED, result)
            elif roi == BallMetrics.HLA and (result > 20 or result < -20):
                if result < 0:
                    sign = -1
                else:
                    sign = 1
                result = self.__fix_out_of_bounds_metric(20, (result * sign), roi)
                result = result * sign
                self.corrections[roi] = True
            # Round all values to one decimal place
            setattr(self, roi, math.floor(float(result)*10)/10)
            logging.debug(f'Cleaned and corrected value: {result}')
        except ValueError as e:
            msg = f'{format(e)}'
        except:
            msg = f"Could not convert value {result} for '{BallData.properties[roi]}' to float 0"
        finally:
            if not msg is None:
                logging.debug(msg)
                self.errors[roi] = msg
                setattr(self, roi, BallData.invalid_value)

    def process_shot_data(self, ocr_result, roi, previous_balldata, launch_monitor):
        msg = None
        result = ''
        try:
            # Strip non ascii chars and commas
            ocr_result = re.sub(r',', r'', re.sub(r'[^\x00-\x7f]', r'', ocr_result))
            logging.debug(f'remove non ASCII {roi}: {ocr_result}')
            cleaned_result = re.findall(r"[-+]?(?:\d*\.*\d+)[LR]?", ocr_result)
            if isinstance(cleaned_result, list or tuple) and len(cleaned_result) > 0:
                cleaned_result = cleaned_result[0]
            logging.debug(f'cleaned result {roi}: {cleaned_result}')
            if len(cleaned_result) > 0:
                cleaned_result = cleaned_result.strip()
            if len(cleaned_result) <= 0:
                logging.debug(f"Value for {BallData.properties[roi]} is empty")
                cleaned_result = '0'
            # Remove any leading '.' sometimes a - is read as a '.'
            result = cleaned_result.lstrip('.')
            if launch_monitor == LaunchMonitor.MEVOPLUS and (roi == BallMetrics.HLA or roi == BallMetrics.SPIN_AXIS):
                result = result.upper()
                if result.endswith('L'):
                    result = -float(result[:-1])
                else:
                    result = float(result[:-1])
            else:
                result = float(result)
            logging.debug(f'result {roi}: {result}')
            # Check values are not 0
            if roi in BallData.must_not_be_zero and result == float(0):
                raise ValueError(f"Value for '{BallData.properties[roi]}' is 0")
            if roi == BallMetrics.VLA and (result <= 0 or result >= 90):
                raise ValueError(f"Value for {BallData.properties[roi]} is <= 0 or >= 90")
            if roi == BallMetrics.TOTAL_SPIN and result <= 100:
                raise ValueError(f"Value for {BallData.properties[roi]} is <= 100")
            # For some reason ball speed sometimes get an extra digit added
            if roi == BallMetrics.SPEED and result > 200:
                result = self.__fix_out_of_bounds_metric(200, result, roi)
                self.corrections[roi] = True
            elif roi == BallMetrics.TOTAL_SPIN and result > 13000:
                result = self.__fix_out_of_bounds_metric(13000, result, roi)
                self.corrections[roi] = True
            elif roi == BallMetrics.CLUB_SPEED and result > 140:
                result = self.__fix_out_of_bounds_metric(140, result, roi)
                self.corrections[roi] = True
            # Round to one decimal place
            setattr(self, roi, math.floor(result*10)/10)
            logging.debug(f'Cleaned and corrected value: {result}')
        except ValueError as e:
            msg = f'{format(e)}'
        except:
            msg = f"Could not convert value {result} for '{BallData.properties[roi]}' to float 0"
        finally:
            if not msg is None:
                logging.debug(msg)
                self.errors[roi] = msg
                setattr(self, roi, BallData.invalid_value)

    def eq(self, other):
        diff_count = 0
        non_zero_found = False
        for roi in self.properties:
            result = getattr(self, roi)
            if result > 0 and not non_zero_found:
                non_zero_found = True
            previous_result = getattr(other, roi)
            if (roi != BallMetrics.BACK_SPIN and roi != BallMetrics.SIDE_SPIN and result != previous_result):
                logging.debug(f'previous_metric: {previous_result} result: {result}')
                diff_count = diff_count + 1
        # Check if all values are 0, some users use practice instead of range and there is a screen flicker
        # that causes an invalid shot with all invalid values so all values are still 0. Check if all values
        # are zero if so ignore the shot
        if not non_zero_found:
            diff_count = 0
            logging.debug(f'All values are 0: ignoring')
        if diff_count > 0:
            logging.debug(f'diff count: {diff_count} -> new shot')
            self.new_shot = True
        return diff_count

    def __fix_out_of_bounds_metric(self, limit, value, roi):
        msg = f"Invalid {BallData.properties[roi]} value: {value} > {limit}"
        corrected_value = value
        while corrected_value > limit:
            corrected_value = math.floor(corrected_value / 10)
        logging.debug(f"{msg}, corrected value: {corrected_value}")
        return corrected_value

    def __smash_factor(self, club_speed, ball_speed):
        return math.ceil((ball_speed / club_speed)*10)/10

    def check_smash_factor(self, selected_club):
        club_speed = getattr(self, BallMetrics.CLUB_SPEED)
        ball_speed = getattr(self, BallMetrics.SPEED)
        if club_speed > 0:
            smash_factor = self.__smash_factor(club_speed, ball_speed)
            if selected_club is not None and selected_club == 'DR':
                logging.debug(f'Selected club {selected_club} is a driver, apply driver smash factor correction')
                # Corrects for Club Speed Misreads on the MLM2PRO related to 5-wood thru Driver where ball speed appears correct.
                if smash_factor > 1.7 and ball_speed > 125.0 and ball_speed < 250:
                    corrected_value = math.floor(ball_speed / 1.48)
                    setattr(self, BallMetrics.CLUB_SPEED, corrected_value)
                    self.corrections[BallMetrics.CLUB_SPEED] = True
                    logging.debug(
                        f"Smash factor: {smash_factor} > 1.7 and ball speed between 125.0 and 250.0, corrected CLUB_SPEED value: {corrected_value}")
                # Corrects for Ball Speed Misreads on the MLM2PRO related to 5-wood thru Driver where Club Speed is correct.
                elif smash_factor <= 0.7 and club_speed > 90 and club_speed < 175:
                    corrected_value = math.floor(club_speed * 1.48)
                    setattr(self, BallMetrics.SPEED, corrected_value)
                    self.corrections[BallMetrics.SPEED] = True
                    logging.debug(
                        f"Smash factor: {smash_factor} <= 0.7 and club speed between 90 and 175, corrected SPEED value: {corrected_value}")
            else:
                logging.debug(f'Selected club {selected_club} is not a driver, apply non driver smash factor correction')
                if smash_factor >= 1.7 and ball_speed >= 100:
                    corrected_value = math.floor(ball_speed/10)
                    setattr(self, BallMetrics.SPEED, corrected_value)
                    self.corrections[BallMetrics.SPEED] = True
                    logging.debug(f"Invalid smash factor value: {smash_factor} > 1.7, corrected  {BallData.properties[BallMetrics.SPEED]} value: {corrected_value}")
                elif smash_factor <= 0.6:
                    corrected_value = math.floor(club_speed/10)
                    setattr(self, BallMetrics.CLUB_SPEED, corrected_value)
                    self.corrections[BallMetrics.CLUB_SPEED] = True
                    logging.debug(f"Invalid smash factor value: {smash_factor} < 0.6, corrected  {BallData.properties[BallMetrics.CLUB_SPEED]} value: {corrected_value}")
        self.back_spin = round(
            self.total_spin * math.cos(math.radians(self.spin_axis)))
        self.side_spin = round(
            self.total_spin * math.sin(math.radians(self.spin_axis)))

import json
from dataclasses import dataclass


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
        BallMetrics.SIDE_SPIN: 'Side Spin'
    }
    rois_properties = [BallMetrics.SPEED,
                       BallMetrics.TOTAL_SPIN,
                       BallMetrics.SPIN_AXIS,
                       BallMetrics.HLA,
                       BallMetrics.VLA,
                       BallMetrics.CLUB_SPEED]
    must_not_be_zero = [BallMetrics.SPEED,
                        BallMetrics.TOTAL_SPIN,
                        BallMetrics.CLUB_SPEED]

    def __init__(self, *initial_data, **kwargs):
        self.good_shot = False
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

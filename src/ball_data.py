import json
import logging


class BallData:
    properties = {
        'speed': 'Ball Speed',
        'spin_axis': 'Spin Rate',
        'total_spin': 'Spin Axis',
        'hla': 'Launch Direction (HLA)',
        'vla': 'Launch Angle (VLA)',
        'club_speed': 'Club Speed',
        'back_spin': 'Back Spin',
        'side_spin': 'Side Spin'
    }
    rois_properties = ['speed', 'spin_axis', 'total_spin', 'hla', 'vla', 'club_speed']
    must_not_be_zero = ['speed', 'total_spin', 'club_speed']

    def __init__(self, *initial_data, **kwargs):
        for key in BallData.properties:
            setattr(self, key, 0)
        for dictionary in initial_data:
            logging.debug(f'dictionary: {dictionary}')
            for key in dictionary:
                logging.debug(f'key: {key}')
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __copy__(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

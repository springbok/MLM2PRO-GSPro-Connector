import json
import os
import logging

class Rois:

    def __init__(self):
        self.values = None
        self.__load()
        self.keys = ["Ball Speed", "Spin Rate", "Spin Axis", "Launch Direction (HLA)", "Launch Angle (VLA)", "Club Speed"]

    def __load(self):
        path = os.path.join(os.getcwd(), 'rois.json')
        logging.info(f"Loading rois from {path}")
        if os.path.isfile(path):
            with open(os.path.join(os.getcwd(), 'settings.json'), "r") as file:
                lines = file.readlines()
                self.values = json.loads(lines)
            logging.info(f"RIOS: {self.values}")

    def write(self):
        with open(os.path.join(os.getcwd(), 'rois.json'), "w") as file:
            file.write(json.dumps(self.values, indent=4))


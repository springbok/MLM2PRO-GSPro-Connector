import json
import os
import logging

class RoisNotUsed:

    def __init__(self, app_paths):
        self.path = app_paths.get_config_path(
            name='rois',
            ext='.json'
        )
        self.values = {}
        self.__load()
        self.keys = ["Ball Speed", "Spin Rate", "Spin Axis", "Launch Direction (HLA)", "Launch Angle (VLA)", "Club Speed"]
        # Mapping between the keys for the ROI's entered by the user and the attributes
        # of our BallData class allowing us to dynamically assign values to the ball data object
        self.ball_data_mapping = {
            "Ball Speed": "speed",
            "Spin Rate": "total_spin",
            "Spin Axis": "spin_axis",
            "Launch Direction (HLA)": "hla",
            "Launch Angle (VLA)": "vla",
            "Club Speed": "club_speed"
        }
        self.must_not_be_zero = ["speed", "total_spin", "club_speed"]

    def __load(self):
        logging.info(f"Loading rois from {self.path}")
        if os.path.isfile(self.path):
            with open(self.path, "r") as file:
                lines = file.readlines()
                cleaned_lines = [line.split("//")[0].strip() for line in lines if not line.strip().startswith("//")]
                cleaned_json = "\n".join(cleaned_lines)
                self.values = json.loads(cleaned_json)
            logging.info(f"RIOS: {self.values}")

    def write(self):
        with open(self.path, "w") as file:
            file.write(json.dumps(self.values, indent=4))


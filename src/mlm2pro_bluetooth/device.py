from src.mlm2pro_bluetooth.utils import MLM2PROUtils


class MLM2PRODevice:

    def __init__(self):
        self.user_token = "0"
        self.device_status = "NOTCONNECTED"
        self.club_selection = "NONE"
        self.handedness = 1
        self.ball_type = 2
        self.environment = 0
        self.altitude_metres = 0.0
        self.temperature_celsius = 20.0
        self.quit_event = 0
        self.power_mode = 0
        self.serial_number = ""
        self.model = ""
        self.battery = 0
        self.response_message = None
        self.events = None
        self.measurement = None
        self.info_complete = False

    def reset_device_info(self):
        self.serial_number = ""
        self.model = ""
        self.battery = 0
        self.response_message = None
        self.events = None
        self.measurement = None
        self.info_complete = False

    def update_info_complete(self):
        if self.serial_number and self.model and self.battery > 0:
            self.info_complete = True
        else:
            self.info_complete = False

    def update_serial_number(self, serial_number):
        self.serial_number = serial_number
        self.update_info_complete()

    def update_model(self, model):
        self.model = model
        self.update_info_complete()

    def update_battery_level(self, battery_level):
        if battery_level != 0:
            self.battery = battery_level
            self.update_info_complete()

    def update_events(self, events):
        if events is not None:
            self.events = MLM2PROUtils.bytearray_to_int_array(events)

    def update_response_message(self, response_message):
        if response_message is not None:
            self.response_message = MLM2PROUtils.bytearray_to_int_array(response_message)

    def update_measurement(self, measurement):
        if measurement is not None:
            self.measurement = MLM2PROUtils.bytearray_to_int_array(measurement)

    def get_initial_parameters(self, token_input):
        self.user_token = token_input
        print("GetInitialParameters: UserToken: " + self.user_token)

        # Generate required byte arrays
        air_pressure_bytes = MLM2PROUtils.get_air_pressure_bytes(0.0)
        temperature_bytes = MLM2PROUtils.get_temperature_bytes(15.0)
        long_to_uint_to_byte_array = MLM2PROUtils.long_to_uint_to_byte_array(int(self.user_token), True)

        # Concatenate all byte arrays
        concatenated_bytes = bytearray([1, 2, 0, 0]) + air_pressure_bytes + temperature_bytes + long_to_uint_to_byte_array + bytearray([0, 0])

        print("GetInitialParameters: ByteArrayReturned: " + MLM2PROUtils.byte_array_to_hex_string(concatenated_bytes))
        return concatenated_bytes

    def get_parameters_from_settings(self):
        if not self.user_token:
            return None

        altitude = self.altitude_metres if self.altitude_metres is not None else 0.0
        temperature = self.temperature_celsius if self.temperature_celsius is not None else 15.0

        handedness_bytes = [self.handedness] if self.handedness is not None else [1]
        ball_type_bytes = [self.ball_type] if self.ball_type is not None else [2]
        environment_bytes = [self.environment] if self.environment is not None else [0]
        quit_event_bytes = [self.quit_event] if self.quit_event is not None else [0]
        power_mode_bytes = [self.power_mode] if self.power_mode is not None else [0]

        air_pressure_bytes = MLM2PROUtils.get_air_pressure_bytes(altitude)
        temperature_bytes = MLM2PROUtils.get_temperature_bytes(temperature)
        user_token_bytes = MLM2PROUtils.long_to_uint_to_byte_array(int(self.user_token), True)

        concatenated_bytes = handedness_bytes + ball_type_bytes + environment_bytes + [0] + list(air_pressure_bytes) + list(temperature_bytes) + list(user_token_bytes) + quit_event_bytes + power_mode_bytes

        return bytearray(concatenated_bytes)
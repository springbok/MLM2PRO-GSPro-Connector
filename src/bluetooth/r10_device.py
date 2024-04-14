import datetime
import json
import logging
from dataclasses import dataclass
from typing import Optional

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyCharacteristic
from PySide6.QtCore import QUuid, QByteArray, QTimer, Signal

from src.ball_data import BallData
from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase
from src.bluetooth.bluetooth_device_service import BluetoothDeviceService
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.mlm2pro_encryption import MLM2PROEncryption
from src.bluetooth.mlm2pro_secret import MLM2PROSecret
from src.bluetooth.mlm2pro_web_api import MLM2PROWebApi


class R10Device(BluetoothDeviceBase):
    launch_monitor_event = Signal(str)

    HEARTBEAT_INTERVAL = 2000
    R10_HEARTBEAT_INTERVAL = 20000

    MLM2PRO_SEND_INITIAL_PARAMS = 2
    MLM2PRO_AUTH_SUCCESS = 0
    MLM2PRO_RAPSODO_AUTH_FAILED = 1
    MLM2PRO_VALID_WRITE_RESPPONSE = 1
    
    BATTERY_SERVICE_UUID = QBluetoothUuid(QUuid('{0000180f-0000-1000-8000-00805f9b34fb}'))
    BATTERY_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{00002a19-0000-1000-8000-00805f9b34fb}'))
    DEVICE_INFO_SERVICE_UUID = QBluetoothUuid(QUuid('{0000180a-0000-1000-8000-00805f9b34fb}'))
    FIRMWARE_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{00002a28-0000-1000-8000-00805f9b34fb}'))
    MODEL_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{00002a24-0000-1000-8000-00805f9b34fb}'))
    SERIAL_NUMBER_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{00002a25-0000-1000-8000-00805f9b34fb}'))
    DEVICE_INTERFACE_SERVICE = QBluetoothUuid(QUuid('{6A4E2800-667B-11E3-949A-0800200C9A66}'))
    DEVICE_INTERFACE_NOTIFIER = QBluetoothUuid(QUuid('{6A4E2812-667B-11E3-949A-0800200C9A66}'))
    DEVICE_INTERFACE_WRITER = QBluetoothUuid(QUuid('{6A4E2822-667B-11E3-949A-0800200C9A66}'))

    MEASUREMENT_SERVICE_UUID = QBluetoothUuid(QUuid('{6A4E3400-667B-11E3-949A-0800200C9A66}'))
    MEASUREMENT_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{6A4E3401-667B-11E3-949A-0800200C9A66}'))
    CONTROL_POINT_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{6A4E3402-667B-11E3-949A-0800200C9A66}'))
    STATUS_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{6A4E3403-667B-11E3-949A-0800200C9A66}'))

    def __init__(self, device: QBluetoothDeviceInfo):
        self._services: Optional[list[BluetoothDeviceService]] = []
        self._device_info_service: BluetoothDeviceService = BluetoothDeviceService(
            device,
            R10Device.DEVICE_INFO_SERVICE_UUID,
            None, None,
            self._device_info_service_read_handler
        )
        self._device_info_service.services_discovered.connect(self.__read_device_info)
        self._services.append(self._device_info_service)
        super().__init__(device,
                         self._services,
                         R10Device.HEARTBEAT_INTERVAL,
                         R10Device.R10_HEARTBEAT_INTERVAL)

    def _device_info_service_read_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        msg = f'Received data for characteristic {characteristic.uuid().toString()} from {self._ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}'
        print(msg)
        logging.debug(msg)
        decoded_data = data.data().decode('utf-8')
        if characteristic.uuid() == R10Device.SERIAL_NUMBER_CHARACTERISTIC_UUID:
            self._serial_number = decoded_data
            msg = f'Serial number: {self._serial_number}'
        elif characteristic.uuid() == R10Device.FIRMWARE_CHARACTERISTIC_UUID:
            self._firmware_version = decoded_data
            msg = f'Firmware version: {self._firmware_version}'
        elif characteristic.uuid() == R10Device.MODEL_CHARACTERISTIC_UUID:
            self._model = decoded_data
            msg = f'Model: {self._model}'
        else:
            msg = f'Unknown characteristic: {characteristic.uuid().toString()}'
        print(msg)
        logging.debug(msg)

    def __read_device_info(self) -> None:
        msg = f'Reading device info for {self._ble_device.name()} at {self._sensor_address()}'
        print(msg)
        logging.debug(msg)
        self._device_info_service.read_characteristic(R10Device.SERIAL_NUMBER_CHARACTERISTIC_UUID)
        self._device_info_service.read_characteristic(R10Device.FIRMWARE_CHARACTERISTIC_UUID)
        self._device_info_service.read_characteristic(R10Device.MODEL_CHARACTERISTIC_UUID)


'''
        super().__init__(device,
                         R10Device.MEASUREMENT_SERVICE_UUID,
                         R10Device.HEARTBEAT_INTERVAL,
                         R10Device.R10_HEARTBEAT_INTERVAL)
        self._user_token = "0"
        self._ball_type = 2
        self._altitude_metres = 0.0
        self._temperature_celsius = 15.0
        self._notification_uuids = [
            R10Device.CONTROL_POINT_CHARACTERISTIC_UUID,
            R10Device.STATUS_CHARACTERISTIC_UUID,
            R10Device.MEASUREMENT_SERVICE_UUID
        ]
        self._encryption = MLM2PROEncryption()
        self._web_api = MLM2PROWebApi(self._settings.web_api['url'],
                                      MLM2PROSecret.decrypt(self._settings.web_api['secret']))

    def _authenticate(self) -> None:
        print('authenticating')
        logging.debug('Authenticating')
        if self._is_connected() is False:
            self.error.emit('Device not connected')
            return
        if self._service is None:
            self.error.emit('General service not initialized')
            return
        self.status_update.emit('Authenticating...', self._ble_device.name())
        int_to_byte_array = BluetoothUtils.int_to_byte_array(1, True, False)
        encryption_type_bytes = self._encryption.get_encryption_type_bytes()
        key_bytes = self._encryption.get_key_bytes()
        if key_bytes is None:
            self.error.emit('Key bytes not generated')
        b_arr = bytearray(int_to_byte_array + encryption_type_bytes + key_bytes)
        b_arr[:len(int_to_byte_array)] = int_to_byte_array
        b_arr[len(int_to_byte_array):len(int_to_byte_array) + len(encryption_type_bytes)] = encryption_type_bytes
        start_index = len(int_to_byte_array) + len(encryption_type_bytes)
        end_index = start_index + len(key_bytes)
        b_arr[start_index:end_index] = key_bytes
        logging.debug(
            f'----> Writing authentication data: {BluetoothUtils.byte_array_to_hex_string(b_arr)}')
        print(
            f'----> Writing authentication data: {BluetoothUtils.byte_array_to_hex_string(b_arr)}')
        self._write_characteristic(R10Device.AUTH_CHARACTERISTIC_UUID, b_arr)

    def _data_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        """
        `data` GATT data
        """
        if characteristic.uuid() != R10Device.HEARTBEAT_CHARACTERISTIC_UUID:
            print(f'Received data for characteristic {characteristic.uuid().toString()} from {self._ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}')
            logging.debug(f'<---- Received data for characteristic {characteristic.uuid().toString()} from {self._ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}')
        byte_array = data.data()
        if characteristic.uuid() == R10Device.WRITE_RESPONSE_CHARACTERISTIC_UUID:
            self.__process_write_response(byte_array)
        elif characteristic.uuid() == R10Device.HEARTBEAT_CHARACTERISTIC_UUID:
            #print(f'Heartbeat received from MLM2PRO {characteristic.uuid().toString()}')
            #logging.debug(f'Heartbeat received from MLM2PRO {characteristic.uuid().toString()}')
            self._set_next_expected_heartbeat()
        elif characteristic.uuid() == R10Device.EVENTS_CHARACTERISTIC_UUID:
            self.__process_events(byte_array)
        elif characteristic.uuid() == R10Device.MEASUREMENT_CHARACTERISTIC_UUID:
            self.__process_measurement(byte_array)

    def __process_measurement(self, data: bytearray) -> None:
        if not self._armed:
            return
        try:
            msg = f'>>>> Measurement: {BluetoothUtils.byte_array_to_hex_string(data)}'
            print(msg)
            logging.debug(msg)
            decrypted = self._encryption.decrypt(bytes(data))
            if decrypted is None:
                print('Error decrypting data')
                logging.debug('Error decrypting data')
                self.error.emit('Error decrypting data')
                return
            msg = f'>>>> Measurement decrypted data: {BluetoothUtils.byte_array_to_hex_string(decrypted)}'
            print(msg)
            logging.debug(msg)
            msg = f'>>>> Measurement decrypted data: {BluetoothUtils.bytearray_to_int_array(bytearray(decrypted))}'
            print(msg)
            logging.debug(msg)
            shot_data = BallData()
            shot_data.club = self._current_club
            shot_data.from_mlm2pro_bt(bytearray(decrypted))
            self.shot.emit(shot_data)
            msg = f'>>>> Calculated shot data: {shot_data.to_json()}'
            print(msg)
            logging.debug(msg)
        except Exception as e:
            msg = f'Error when decrypting measurement data: {format(e)}'
            print(msg)
            logging.debug(msg)
            self.error.emit(msg)

    def __process_events(self, data: bytearray) -> None:
        try:
            print(f'Processing Event: {BluetoothUtils.byte_array_to_hex_string(data)}')
            logging.debug(f'Processing Event: {BluetoothUtils.byte_array_to_hex_string(data)}')
            decrypted = self._encryption.decrypt(bytes(data))
            if decrypted is None:
                print('Error decrypting data')
                logging.debug('Error decrypting data')
                self.error.emit('Error decrypting data')
                return
            print(f'Decrypted Event {decrypted[0]}: {BluetoothUtils.bytearray_to_int_array(bytearray(decrypted))}')
            event_string = None
            match decrypted[0]:
                case LaunchMonitorEvents.SHOT:
                    event_string = 'SHOT READ'
                    print('Shot event')
                case LaunchMonitorEvents.PROCESSING_SHOT:
                    event_string = 'PROCESSING SHOT'
                    print('Processing shot event')
                case LaunchMonitorEvents.READY:
                    event_string = 'READY'
                    print('Ready event')
                case LaunchMonitorEvents.BATTERY:
                    print('Battery event')
                    logging.debug(f'Battery event: {decrypted[1]}')
                    self.update_battery.emit(int(decrypted[1]))
                case LaunchMonitorEvents.MISREAD_OR_DISARMED:
                    if decrypted[1] == 0:
                        print('Misread event')
                        #event_string = 'MISREAD'
                        return
                    elif decrypted[1] == 1:
                        print('Disarmed event')
                        event_string = 'DISARMED'
                case _:
                    print('Unknown event')
            if event_string is not None:
                self.launch_monitor_event.emit(event_string)
                logging.debug(f'Launch monitor event: {event_string}')


        except Exception as e:
            msg = f'Error when decrypting events data {format(e)}'
            print(msg)
            logging.debug(msg)
            self.error.emit(msg)

    def __process_write_response(self, data: bytearray) -> None:
        int_array = BluetoothUtils.bytearray_to_int_array(data)
        print(f'Write response: {int_array}')
        logging.debug(f'Write response: {int_array}')
        if len(data) >= 2:
            if len(data) > 2:
                if data[0] == R10Device.MLM2PRO_SEND_INITIAL_PARAMS:
                    logging.debug(f'Authentication requested {data[0]}: Initial parameters need to be sent to MLM2PRO')
                    print(f'Auth requested: Initial parameters need to be sent to MLM2PRO {data[0]}')
                    if data[1] != R10Device.MLM2PRO_AUTH_SUCCESS or len(data) < 4:
                        print(f'Auth failed: {data[1]}')
                        logging.debug(print(f'Authentication failed: {data[1]}'))
                        token_expiry = self.__token_expiry_date_state(self._settings.web_api['token_expiry'])
                        if data[1] == R10Device.MLM2PRO_RAPSODO_AUTH_FAILED:
                            self.error.emit(f'Your 3rd party authorisation expired on {token_expiry}, please re-authorise in the Rapsodo app and try again once that has been done.')
                            return
                        else:
                            self.error.emit('Authentication failed.')
                            return
                    print('Auth success, send initial params')
                    logging.debug('Authentication success, send initial params')
                    QTimer().singleShot(0, lambda: self.__send_initial_params(data))
                elif data[0] == R10Device.MLM2PRO_AUTH_SUCCESS:
                    logging.debug(f'Authentication successful {data[0]}')
                    print(f'Authentication successful {data[0]}')
                    self.launch_monitor_connected.emit()
                else:
                    logging.debug(f'Invalid Write response: {int_array}')
                    print(f'Invalid Write response: {int_array}')
            else:
                logging.debug('Connected to MLM2PRO, initial parameters not required')
                self.launch_monitor_connected.emit()

    def _heartbeat(self) -> None:
        if self._is_connected() and self._armed:
            if self._heartbeat_overdue:
                # heartbeat not received within 20 seconds, reset subscriptions
                print(f'Heartbeat not received for {R10Device.R10_HEARTBEAT_INTERVAL} seconds, resubscribing...')
                logging.debug(f'Heartbeat not received for {R10Device.R10_HEARTBEAT_INTERVAL} seconds, resubscribing...')
                self._set_next_expected_heartbeat()
            self._write_characteristic(R10Device.HEARTBEAT_CHARACTERISTIC_UUID, bytearray([0x01]))

    def __send_initial_params(self, data: bytearray) -> None:
        byte_array = data[2:]
        print(f'byte array: {byte_array}')
        byte_array2 = byte_array[:4]
        user_id = BluetoothUtils.bytes_to_int(byte_array2, True)
        logging.debug(f'User ID generated from device: {user_id}')
        print(f'User ID generated from device: {user_id}')
        self._settings.web_api['user_id'] = user_id
        self._settings.save()
        self.__update_user_token(user_id)
        params = self.__get_initial_parameters(self._settings.web_api['token'])
        self.__write_config(params)

    def __update_user_token(self, user_id: int) -> None:
        print(f'updating user token: {user_id}')
        logging.debug(f'Updating user token: {user_id}')
        result = self._web_api.send_request(user_id)
        print(f'update user token response: {result}')
        logging.debug(f'Update user token response: {result}')
        if result is not None:
            response = json.loads(result)
            print('User token updated successfully')
            logging.debug(f'User token updated successfully, token: {response["user"]["token"]} expiry: {response["user"]["expireDate"]} device id: {response["user"]["id"]}')
            self._user_token = response['user']['token']
            self._settings.web_api['token'] = response['user']['token']
            self._settings.web_api['token_expiry'] = response['user']['expireDate']
            self._settings.web_api['device_id'] = response['user']['id']
            self._settings.save()
            self.__token_expiry_date_state(response['user']['expireDate'])
        else:
            logging.debug('Failed to update user token')
            self.error.emit('Failed to update user token from web API')

    def __get_initial_parameters(self, token_input: int) -> bytearray:
        print(f"GetInitialParameters: UserToken: {token_input}")
        # Generate required byte arrays
        air_pressure_bytes = BluetoothUtils.get_air_pressure_bytes(0.0)
        temperature_bytes = BluetoothUtils.get_temperature_bytes(self._temperature_celsius)
        long_to_uint_to_byte_array = BluetoothUtils.long_to_uint_to_byte_array(int(token_input), True)
        # Concatenate all byte arrays
        concatenated_bytes = bytearray([1, 2, 0, 0]) + air_pressure_bytes + temperature_bytes + long_to_uint_to_byte_array + bytearray([0, 0])
        print("GetInitialParameters: ByteArrayReturned: " + BluetoothUtils.byte_array_to_hex_string(concatenated_bytes))
        return concatenated_bytes

    def __write_config(self, data: bytearray) -> None:
        print(f'Write config: {BluetoothUtils.byte_array_to_hex_string(data)}')
        logging.debug(f'Config data: {BluetoothUtils.byte_array_to_hex_string(data)}')
        config_data = bytearray(self._encryption.encrypt(data))
        logging.debug(
            f'----> Writing config data: {BluetoothUtils.byte_array_to_hex_string(config_data)}')
        print(
            f'----> Writing config data: {BluetoothUtils.byte_array_to_hex_string(config_data)}')
        self._write_characteristic(R10Device.CONFIGURE_CHARACTERISTIC_UUID, config_data)

    def _disarm_device(self) -> None:
        byte_array = bytearray.fromhex("010D0000000000")
        self.__write_command(byte_array)
        print(f'Disarm command sent')
        logging.debug(f'Disarm command sent')

    def _arm_device(self) -> None:
        byte_array = bytearray.fromhex("010D0001000000")
        self.__write_command(byte_array)
        print(f'Arm command sent')
        logging.debug(f'Arm command sent')

    def __write_command(self, data: bytearray) -> None:
        print(f'Write command: {BluetoothUtils.byte_array_to_hex_string(data)}')
        logging.debug(f'Write command: {BluetoothUtils.byte_array_to_hex_string(data)}')
        command_data = bytearray(self._encryption.encrypt(data))
        logging.debug(
            f'----> Writing config data: {BluetoothUtils.byte_array_to_hex_string(command_data)}')
        print(
            f'----> Writing config data: {BluetoothUtils.byte_array_to_hex_string(command_data)}')
        self._write_characteristic(R10Device.COMMAND_CHARACTERISTIC_UUID, command_data)

    def __token_expiry_date_state(self, token_expiry: float) -> str:
        if token_expiry <= 0:
            return 'Uknown'
        # Assuming token expiry is the Unix timestamp
        expire_date = datetime.datetime.fromtimestamp(token_expiry)
        # Convert to local datetime
        local_expire_date = expire_date.astimezone()
        # Get current datetime
        now = datetime.datetime.now().astimezone()
        # Check if expire_date is in the future and less than 3 hours from now
        token_state = TokenExpiryStates.TOKEN_EXPIRY_OK
        if now < local_expire_date < now + datetime.timedelta(hours=3):
            token_state = TokenExpiryStates.TOKEN_EXPIRY_3HOURS
        elif local_expire_date < now:
            token_state = TokenExpiryStates.TOKEN_EXPIRED
        expire_date_str = local_expire_date.strftime("%Y-%m-%d %H:%M:%S")
        self.token_expiry.emit(token_state, expire_date_str)
        return expire_date_str
'''
import json
import logging

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyCharacteristic
from PySide6.QtCore import QUuid, QByteArray, QTimer

from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.mlm2pro_encryption import MLM2PROEncryption
from src.bluetooth.mlm2pro_secret import MLM2PROSecret
from src.bluetooth.mlm2pro_web_api import MLM2PROWebApi


class MLM2PRODevice(BluetoothDeviceBase):
    HEARTBEAT_INTERVAL = 2000
    MLM2PRO_HEARTBEAT_INTERVAL = 20000

    MLM2PRO_SEND_INITIAL_PARAMS = 2
    MLM2PRO_AUTH_SUCCESS = 0
    MLM2PRO_RAPSODO_AUTH_FAILED = 1
    MLM2PRO_VALID_WRITE_RESPPONSE = 1

    SERVICE_UUID = QBluetoothUuid(QUuid('{DAF9B2A4-E4DB-4BE4-816D-298A050F25CD}'))
    #firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'
    AUTH_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{B1E9CE5B-48C8-4A28-89DD-12FFD779F5E1}'))
    COMMAND_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{1EA0FA51-1649-4603-9C5F-59C940323471}'))
    CONFIGURE_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{DF5990CF-47FB-4115-8FDD-40061D40AF84}'))
    EVENTS_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{02E525FD-7960-4EF0-BFB7-DE0F514518FF}'))
    HEARTBEAT_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{EF6A028E-F78B-47A4-B56C-DDA6DAE85CBF}'))
    MEASUREMENT_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{76830BCE-B9A7-4F69-AEAA-FD5B9F6B0965}'))
    WRITE_RESPONSE_CHARACTERISTIC_UUID = QBluetoothUuid(QUuid('{CFBBCB0D-7121-4BC2-BF54-8284166D61F0}'))

    def __init__(self, device: QBluetoothDeviceInfo):
        super().__init__(device,
                         MLM2PRODevice.SERVICE_UUID,
                         MLM2PRODevice.HEARTBEAT_INTERVAL,
                         MLM2PRODevice.MLM2PRO_HEARTBEAT_INTERVAL)
        self._user_token = "0"
        self._ball_type = 2
        self._altitude_metres = 0.0
        self._temperature_celsius = 15.0
        self._notification_uuids = [
            MLM2PRODevice.EVENTS_CHARACTERISTIC_UUID,
            MLM2PRODevice.HEARTBEAT_CHARACTERISTIC_UUID,
            MLM2PRODevice.WRITE_RESPONSE_CHARACTERISTIC_UUID,
            MLM2PRODevice.MEASUREMENT_CHARACTERISTIC_UUID
        ]
        self._encryption = MLM2PROEncryption()
        self._web_api = MLM2PROWebApi(self._settings.web_api['url'], MLM2PROSecret.decrypt(self._settings.web_api['secret']))

    def _authenticate(self):
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
        if key_bytes is None: self.error.emit('Key bytes not generated')
        b_arr = bytearray(int_to_byte_array + encryption_type_bytes + key_bytes)
        b_arr[:len(int_to_byte_array)] = int_to_byte_array
        b_arr[len(int_to_byte_array):len(int_to_byte_array) + len(encryption_type_bytes)] = encryption_type_bytes
        start_index = len(int_to_byte_array) + len(encryption_type_bytes)
        end_index = start_index + len(key_bytes)
        b_arr[start_index:end_index] = key_bytes
        self._write_characteristic(MLM2PRODevice.AUTH_CHARACTERISTIC_UUID, b_arr)

    def _data_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'Received data for characteristic {characteristic.uuid().toString()}from {self._ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}')
        logging.debug(f'Received data for characteristic {characteristic.uuid().toString()}from {self._ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}')
        byte_array = data.data()
        if characteristic.uuid() == MLM2PRODevice.WRITE_RESPONSE_CHARACTERISTIC_UUID:
            int_array = BluetoothUtils.bytearray_to_int_array(byte_array)
            print(f'Write response {characteristic.uuid}: {int_array}')
            logging.debug(f'Write response {characteristic.uuid}: {int_array}')
            self.__process_write_response(int_array)
        elif characteristic.uuid() == MLM2PRODevice.HEARTBEAT_CHARACTERISTIC_UUID:
            print(f'Heartbeat received from MLM2PRO {characteristic.uuid}')
            logging.debug(f'Heartbeat received from MLM2PRO {characteristic.uuid}')
            self._set_next_expected_heartbeat()

    def __process_write_response(self, data: list[int]) -> None:
        if len(data) >= 2:
            if len(data) > 2:
                if data[0] == MLM2PRODevice.MLM2PRO_SEND_INITIAL_PARAMS:
                    logging.debug(f'Authentication requested {data[0]}: Initial parameters need to be sent to MLM2PRO')
                    print(f'Auth requested: Initial parameters need to be sent to MLM2PRO {data[0]}')
                    if data[1] != MLM2PRODevice.MLM2PRO_AUTH_SUCCESS or len(data) < 4:
                        print(f'Auth failed: {data[1]}')
                        if data[1] == MLM2PRODevice.MLM2PRO_RAPSODO_AUTH_FAILED:
                            self.error.emit('Awesome Golf authorisation has expired, please re-authorise in the Rapsodo app and try again once that has been done.')
                            return
                        else:
                            self.error.emit('Authentication failed.')
                            return
                    print('Auth success, send initial params')
                    logging.debug('Authentication success, send initial params')
                    QTimer().singleShot(0, lambda: self.__send_initial_params(data))
                    # Start heartbeat
                    self._heartbeat_timer.start()
            else:
                print('Connected to MLM2PRO, initial parameters not required')
                
    def _heartbeat(self):
        print('Sending heartbeat')
        if self._is_connected():
            if self._heartbeat_overdue:
                # heartbeat not received within 20 seconds, reset subscriptions
                print(f'Heartbeat not received for {MLM2PRODevice.MLM2PRO_HEARTBEAT_INTERVAL} seconds, resubscribing...')
                logging.debug(f'Heartbeat not received for {MLM2PRODevice.MLM2PRO_HEARTBEAT_INTERVAL} seconds, resubscribing...')
                self._set_next_expected_heartbeat()
            self._write_characteristic(MLM2PRODevice.HEARTBEAT_CHARACTERISTIC_UUID, bytearray([0x01]))

    def __send_initial_params(self, data):
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
        print(f'Initial parameters: {params}')
        self.__write_config(params)

    def __update_user_token(self, user_id: int):
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
        else:
            logging.debug('Failed to update user token')
            self.error.emit('Failed to update user token from web API')

    def __get_initial_parameters(self, token_input):
        print("GetInitialParameters: UserToken: " + token_input)
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
        logging.debug(f'Write config: {BluetoothUtils.byte_array_to_hex_string(data)}')
        self._write_characteristic(MLM2PRODevice.CONFIGURE_CHARACTERISTIC_UUID,
                                   QByteArray(self._encryption.encrypt(data)))


import logging
import struct
from typing import Optional

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyCharacteristic
from PySide6.QtCore import QUuid, QByteArray, Signal
from cobs import cobs
from google.protobuf.message import Message

from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase
from src.bluetooth.bluetooth_device_service import BluetoothDeviceService
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.r10_pb2 import WrapperProto, LaunchMonitorService, WakeUpRequest, StatusRequest


class R10Device(BluetoothDeviceBase):

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
            None,
            None,
            self._device_info_service_read_handler
        )
        self._device_info_service.services_discovered.connect(self._services_discovered)
        self._services.append(self._device_info_service)
        self._battery_service: BluetoothDeviceService = BluetoothDeviceService(
            device,
            R10Device.BATTERY_SERVICE_UUID,
            [R10Device.BATTERY_CHARACTERISTIC_UUID],
            self._battery_info_handler,
            None
        )
        self._services.append(self._battery_service)
        self._interface_service: BluetoothDeviceService = BluetoothDeviceService(
            device,
            R10Device.DEVICE_INTERFACE_SERVICE,
            [R10Device.DEVICE_INTERFACE_NOTIFIER],
            self._interface_handler,
            None
        )
        self._interface_service.notifications_subscribed.connect(self._notifications_subscribed)
        self._services.append(self._interface_service)
        super().__init__(device,
                         self._services,
                         R10Device.HEARTBEAT_INTERVAL,
                         R10Device.R10_HEARTBEAT_INTERVAL)
        self._interface_service_subscribed = False
        self._handshake_complete = False
        self._counter = 0
        self._current_message = bytearray()
        self._header = bytearray([0x00])

    def _device_info_service_read_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        error = False
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
            error = True
            msg = f'Unknown characteristic: {characteristic.uuid().toString()}'
        print(msg)
        logging.debug(msg)

    def _services_discovered(self, service: QBluetoothUuid) -> None:
        if service == R10Device.DEVICE_INFO_SERVICE_UUID:
            msg = f'Reading device info for {self._ble_device.name()} at {self._sensor_address()}'
            print(msg)
            logging.debug(msg)
            self._device_info_service.read_characteristic(R10Device.SERIAL_NUMBER_CHARACTERISTIC_UUID)
            self._device_info_service.read_characteristic(R10Device.FIRMWARE_CHARACTERISTIC_UUID)
            self._device_info_service.read_characteristic(R10Device.MODEL_CHARACTERISTIC_UUID)

    def _notifications_subscribed(self, service: QBluetoothUuid) -> None:
        msg = f'Subscribed to notifications for service: {service.toString()} for {self._ble_device.name()} at {self._sensor_address()}'
        print(msg)
        logging.debug(msg)
        if service == R10Device.DEVICE_INTERFACE_SERVICE:
            # Do handshake
            message = bytearray.fromhex("000000000000000000010000")
            msg = f'----> Starting handshake: {BluetoothUtils.byte_array_to_hex_string(message)}'
            print(msg)
            logging.debug(msg)
            self._header = bytearray([0x00])
            self.__send_bytes(message)
            #self._interface_service_subscribed = True

    def _battery_info_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        msg = f'<---- (battery) Received data for characteristic {characteristic.uuid().toString()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}'
        print(msg)
        logging.debug(msg)
        self.update_battery.emit(int(data.data()[0]))
        msg = f'Battery level: {int(data.data()[0])}'
        print(msg)
        logging.debug(msg)

    def _interface_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        msg = f'<---- (_interface_handler) Received data for characteristic {characteristic.uuid().toString()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}'
        if characteristic.uuid() == R10Device.DEVICE_INTERFACE_NOTIFIER:
            # Continue handshake
            header = data.data()[0]
            message_data = data.data()[1:]
            msg_hex = BluetoothUtils.byte_array_to_hex_string(message_data)
            if header == 0 or self._handshake_complete is False:
                if msg_hex.startswith("010000000000000000010000"):
                    msg = f'<---- (interface)(ble read) Received handshake message: {msg_hex} header: {header}'
                    print(msg)
                    logging.debug(msg)
                    int_array = BluetoothUtils.bytearray_to_int_array(message_data)
                    message = bytearray.fromhex("00")
                    msg = f'----> Continue handshake: {BluetoothUtils.byte_array_to_hex_string(message)}'
                    print(msg)
                    logging.debug(msg)
                    self._header = bytearray([message_data[12]])
                    self.__send_bytes(message)
                    self._handshake_complete = True
                    self.__setup_measurement_service()
                    self.__wake_device()
                    self.__status_request()
            else:
                read_complete = False
                if message_data[-1] == 0x00:
                    read_complete = True
                    message_data = message_data[:-1]
                if len(message_data) > 0 and message_data[0] == 0x00:
                    self._current_message.clear()
                    message_data = message_data[1:]
                self._current_message.extend(message_data)
                if read_complete and len(self._current_message) > 0:
                    msg = f'<---- (interface)(ble read)(encoded) Received data for characteristic {characteristic.uuid().toString()}: {BluetoothUtils.byte_array_to_hex_string(self._current_message)}'
                    print(msg)
                    logging.debug(msg)
                    decoded = bytearray(cobs.decode(self._current_message))
                    msg = f'<---- (interface)(ble read)(decoded): {BluetoothUtils.byte_array_to_hex_string(decoded)}'
                    print(msg)
                    logging.debug(msg)
                    self.__process_message(decoded)

    def __setup_measurement_service(self) -> None:
        self._measurement_service: BluetoothDeviceService = BluetoothDeviceService(
            self._ble_device,
            R10Device.MEASUREMENT_SERVICE_UUID,
            [R10Device.MEASUREMENT_CHARACTERISTIC_UUID],
            self._measurement_handler,
            None
        )
        self._services.append(self._measurement_service)
        self._connect_to_service(self._measurement_service)

    def _measurement_handler(self, characteristic: QLowEnergyCharacteristic, data: QByteArray) -> None:
        msg = f'<---- (measurements handler) Received data for characteristic {characteristic.uuid().toString()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}'
        print(msg)
        logging.debug(msg)

    def __process_message(self, data: bytearray) -> None:
        supplied_crc = int.from_bytes(data[-2:], byteorder='little')
        calculated_crc = BluetoothUtils.checksum(data[:-2])
        print(f'(__process_message)Processing message: {BluetoothUtils.byte_array_to_hex_string(data)} calculated_crc: {calculated_crc} supplied_crc: {supplied_crc}')
        if calculated_crc != supplied_crc:
            msg = f'Checksum error: {BluetoothUtils.byte_array_to_hex_string(data)}'
            print(msg)
            logging.debug(msg)
            self.error.emit(msg)
        else:
            message_data = data[2:-2]
            ack_body = bytearray([0x00])
            hex_msg = BluetoothUtils.to_hex_string(message_data)
            print(f'(__process_message)hex_msg: {hex_msg}')
            if hex_msg.upper().startswith("A013"):
                # device info
                print(f'A013 - device info')
            elif hex_msg.upper().startswith("BA13"):
                # config
                print(f'BA13 - config')
            elif hex_msg.upper().startswith("B413") or hex_msg.startswith("B313"):
                ack_body.extend(message_data[2:4])
                ack_body.extend(bytearray.fromhex("00000000000000"))
                proto = WrapperProto()
                proto.ParseFromString(bytes(message_data[16:]))
                print(f'(__process_message) proto: {proto}')
                if hex_msg.upper().startswith("B413"):
                    print(f'B413 - protobuf')
                    # all protobuf responses
                    counter = int.from_bytes(message_data[2:4], byteorder='little')
                    self.__handle_protobuf_response(proto)
                else:
                    print(f'B313 - protobuf')
                    # all protobuf requests
                    self.__handle_protbuf_request(proto)
            self.__acknowledge_message(message_data, ack_body)

    def __handle_protbuf_request(self, request: Message) -> None:
        print(f'__handle_protbuf_request: {request}')

    def __handle_protobuf_response(self, request: Message):
        msg = f'__handle_protobuf_response: {request}'
        print(msg)
        logging.debug(msg)
        if request.service.HasField('status_response'):
            state = str(request.service.status_response.state).strip().replace('state: ', '')
            msg = f'Status response: {state}'
            print(msg)
            logging.debug(msg)
            self.launch_monitor_event.emit(state)

    def __acknowledge_message(self, data: bytearray, response: bytearray) -> None:
        print(f'acknowledge message: {BluetoothUtils.byte_array_to_hex_string(data)} response: {BluetoothUtils.byte_array_to_hex_string(response)}')
        result = bytearray.fromhex("8813") + data[:2] + response
        self.__write_message(result)

    def __status_request(self) -> None:
        print(f'Status request')
        logging.debug(f'Status request')
        wrapper_proto = WrapperProto()
        launch_monitor_service = LaunchMonitorService()
        status_request = StatusRequest()
        launch_monitor_service.status_request.CopyFrom(status_request)
        wrapper_proto.service.CopyFrom(launch_monitor_service)
        self.__send_protobuf_request(wrapper_proto)

    def __send_protobuf_request(self, proto: Message) -> None:
        bytes = proto.SerializeToString()
        print(f'protobuf request: {BluetoothUtils.byte_array_to_hex_string(bytes)}')
        l = len(bytes)
        full_msg = bytearray.fromhex("B313") + \
                  BluetoothUtils.int_to_byte_array(self._counter, True) + \
                  bytearray([0x00, 0x00]) + \
                  BluetoothUtils.int_to_byte_array(l, True) + \
                  BluetoothUtils.int_to_byte_array(l, True) + \
                  bytes
        self._counter += 1
        self.__write_message(full_msg)

    def __write_message(self, data: bytearray) -> None:
        msg = f'----> (raw) Writing message: {BluetoothUtils.byte_array_to_hex_string(data)}'
        print(msg)
        logging.debug(msg)
        # Length of message + 2 bytes for length field + 2 bytes for crc field
        length = 2 + len(data) + 2
        bytes_with_length = struct.pack('<H', length) + data
        checksum = BluetoothUtils.checksum(bytearray(bytes_with_length))
        full_frame = bytearray(bytes_with_length) + bytearray(struct.pack('<H', checksum))

        #length_bytes = int.to_bytes(length, byteorder='little')
        #checksum = BluetoothUtils.checksum(data)
        #print(f'checksum: {checksum} length: {length} length_bytes:{length_bytes.hex()}')
        #checksum_bytes = int.to_bytes(checksum, byteorder='little')
        #print(f'checksum: {checksum} length: {length} length_bytes:{length_bytes.hex()} checksum_bytes:{checksum_bytes.hex()}')
        #full_frame = length_bytes + bytes + checksum_bytes
        msg = f'----> (framed) Writing message: {BluetoothUtils.byte_array_to_hex_string(full_frame)}'
        print(msg)
        logging.debug(msg)
        encoded = bytearray([0x00]) + bytearray(cobs.encode(full_frame)) + bytearray([0x00])
        msg = f'----> (encoded) Writing message: {BluetoothUtils.byte_array_to_hex_string(encoded)}'
        print(msg)
        logging.debug(msg)
        while len(encoded) > 19:
            self.__send_bytes(encoded[:19])
            encoded = encoded[19:]
        if len(encoded) > 0:
            self.__send_bytes(encoded)

    def __send_bytes(self, data: bytearray) -> None:
        message = self._header + data
        msg = f'----> (ble write) Writing message: {BluetoothUtils.byte_array_to_hex_string(message)} header: {BluetoothUtils.byte_array_to_hex_string(self._header)}'
        print(msg)
        logging.debug(msg)
        self._interface_service.write_characteristic(R10Device.DEVICE_INTERFACE_WRITER, message)

    def __wake_device(self) -> None:
        msg = 'Wake device'
        print(msg)
        logging.debug(msg)
        wrapper_proto = WrapperProto()
        launch_monitor_service = LaunchMonitorService()
        wake_up_request = WakeUpRequest()
        launch_monitor_service.wake_up_request.CopyFrom(wake_up_request)
        wrapper_proto.service.CopyFrom(launch_monitor_service)
        self.__send_protobuf_request(wrapper_proto)

    def _heartbeat(self) -> None:
        if self._is_connected() and self._interface_service_subscribed:
            if self._is_connected() and self._armed:
                if self._heartbeat_overdue:
                    self._set_next_expected_heartbeat()
                    print(f'Heartbeat not received for {R10Device.R10_HEARTBEAT_INTERVAL} seconds, resubscribing...')
                    logging.debug(f'Heartbeat not received for {R10Device.R10_HEARTBEAT_INTERVAL} seconds, resubscribing...')
            self._interface_service.write_characteristic(R10Device.DEVICE_INTERFACE_WRITER, bytearray([0x01]))

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
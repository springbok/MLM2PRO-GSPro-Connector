import logging
import struct
from typing import Optional

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyCharacteristic
from PySide6.QtCore import QUuid, QByteArray
from cobs import cobs
from google.protobuf.message import Message

from src.ball_data import BallData
from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase
from src.bluetooth.bluetooth_device_service import BluetoothDeviceService
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.r10_pb2 import WrapperProto, LaunchMonitorService, WakeUpRequest, StatusRequest, TiltRequest, \
    StartTiltCalibrationRequest, EventSharing, SubscribeRequest, AlertMessage, AlertNotification, ShotConfigRequest, \
    WakeUpResponse, State, Tilt, SubscribeResponse, AlertDetails, Metrics


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
        self.process_shots = []

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
        print(msg)
        logging.debug(msg)
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
            else:
                read_complete = False
                if message_data[-1] == 0x00:
                    print(f'----> (interface)(ble read) Received last byte {message_data[-1]}')
                    read_complete = True
                    message_data = message_data[:-1]
                if len(message_data) > 0 and message_data[0] == 0x00:
                    print(f'----> (interface)(ble read) first byte 0x00')
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
                    self._current_message.clear()
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
            #self.error.emit(msg)
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
            elif hex_msg.upper().startswith("B413") or hex_msg.upper().startswith("B313"):
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
        msg = f'__handle_protbuf_request: {request}'
        print(msg)
        #logging.debug(msg)
        if request.HasField('event'):
            if request.event.HasField('notification'):
                response = AlertDetails()
                response.ParseFromString(request.event.notification.AlertNotification.SerializeToString())
                print(f'x-x-x-x-x-x-x notification: {response}')
                if response.HasField('tilt_calibration'):
                    print('Tile calibration done, get tilt')
                    self.__get_device_tilt()
                elif response.HasField('state') and not response.HasField('metrics'):
                    state = State()
                    state.ParseFromString(response.state.SerializeToString())
                    self.__process_state_change(state)
                    if state.state == state.ERROR and response.HasField('error'):
                        logging.debug(f'Error: {response.error}')
                elif response.HasField('metrics'):
                    print('>>>>>>>>>>>>>>>  Metrics received')
                    metrics = Metrics()
                    metrics.ParseFromString(response.metrics.SerializeToString())
                    print(f'>>>>>>>>>>>>>>>  Metrics: {metrics}')
                    if len(self.process_shots) > 0 and metrics.shot_id == self.process_shots[-1]:
                        logging.debug(f"<><><><>Received duplicate shot data {metrics.shot_id} == {self.process_shots[-1]}.  Ignoring")
                    else:
                        if self._current_club == 'PT':
                            msg = f'>>>> Putter selected, ignoring shot.'
                            print(msg)
                            logging.debug(msg)
                            return
                        self.process_shots.append(metrics.shot_id)
                        msg = f">>>>>>> Received shot data from device: {metrics}"
                        logging.debug(msg)
                        print(msg)
                        ball_data = BallData()
                        ball_data.club = self._current_club
                        ball_data.from_r10_bt(metrics.ball_metrics, metrics.club_metrics)
                        msg = f'>>>>>>>  Ball data: {ball_data.to_json()}'
                        print(msg)
                        logging.debug(msg)
                        self.shot.emit(ball_data)


    def __handle_protobuf_response(self, request: Message):
        #msg = f'__handle_protobuf_response: {request}'
        #print(msg)
        #logging.debug(msg)
        if request.HasField('service'):
            if request.service.HasField('status_response'):
                response = State()
                response.ParseFromString(request.service.status_response.state.SerializeToString())
                self.__process_state_change(response)
            elif request.service.HasField('tilt_response'):
                response = Tilt()
                response.ParseFromString(request.service.tilt_response.tilt.SerializeToString())
                msg = f'Tilt roll: {response.roll} pitch: {response.pitch}'
                print(msg)
                logging.debug(msg)
            elif request.service.HasField('wake_up_response'):
                response = WakeUpResponse()
                response.ParseFromString(request.SerializeToString())
                if response.status == response.SUCCESS:
                    msg = f'Wakeup response SUCCESS: {response}'
                    print(msg)
                    logging.debug(msg)
                    self.__status_request()
                    self.__subscribe_to_alerts()
                else:
                    self.error.emit(f'Could not wake the device')
        elif request.HasField('event'):
            if request.event.HasField('subscribe_respose'):
                response = SubscribeResponse()
                response.ParseFromString(request.event.subscribe_respose.SerializeToString())
                msg = f'Status response: {response} alert_status: {response.alert_status}'
                print(msg)
                logging.debug(msg)
                if response.alert_status[0].subscribe_status == 0:
                    msg = 'Subscribed to alerts'
                    print(msg)
                    logging.debug(msg)
                    self.__start_tilt_calibration()
                    self.__send_shot_config()
                    self.launch_monitor_connected.emit()

    def __process_state_change(self, state: State) -> None:
        str_state = ''
        if state.state == state.INTERFERENCE_TEST:
            str_state = 'INTERFERENCE TEST'
            self.__get_device_tilt()
        elif state.state == state.WAITING:
            str_state = 'WAITING'
        elif state.state == state.STANDBY:
            str_state = 'STANDBY'
            msg = 'Device is in standby mode, wake it up'
            print(msg)
            logging.debug(msg)
            self.__wake_device()
        elif state.state == state.RECORDING:
            str_state = 'RECORDING'
        elif state.state == state.PROCESSING:
            str_state = 'PROCESSING'
        elif state.state == state.ERROR:
            str_state = 'ERROR'
        else:
            str_state = 'UNKNOWN'
        msg = f'Status response: {str_state}'
        print(msg)
        logging.debug(msg)
        self.launch_monitor_event.emit(str_state)

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

    def __get_device_tilt(self) -> None:
        print(f'Device Tilt request')
        logging.debug(f'Device Tilt request')
        wrapper_proto = WrapperProto()
        launch_monitor_service = LaunchMonitorService()
        tilt_request = TiltRequest()
        launch_monitor_service.tilt_request.CopyFrom(tilt_request)
        wrapper_proto.service.CopyFrom(launch_monitor_service)
        self.__send_protobuf_request(wrapper_proto)

    def __start_tilt_calibration(self) -> None:
        print(f'Tilt Calibration request')
        logging.debug(f'Tilt Calibration request')
        wrapper_proto = WrapperProto()
        launch_monitor_service = LaunchMonitorService()
        start_tilt_calibration_request = StartTiltCalibrationRequest()
        launch_monitor_service.start_tilt_cal_request.CopyFrom(start_tilt_calibration_request)
        wrapper_proto.service.CopyFrom(launch_monitor_service)
        self.__send_protobuf_request(wrapper_proto)

    def __subscribe_to_alerts(self) -> None:
        print(f'Subscribe to Alerts request')
        logging.debug(f'Subscribe to Alerts request')
        wrapper_proto = WrapperProto()
        event_sharing = EventSharing()
        subscribe_request = SubscribeRequest()
        alert_message = AlertMessage()
        alert_message.type = AlertNotification.LAUNCH_MONITOR
        subscribe_request.alerts.extend([alert_message])
        event_sharing.subscribe_request.CopyFrom(subscribe_request)
        wrapper_proto.event.CopyFrom(event_sharing)
        self.__send_protobuf_request(wrapper_proto)

    def __send_shot_config(self) -> None:
        print(f'Send Shot Config request')
        logging.debug(f'Send Shot Config request')
        wrapper_proto = WrapperProto()
        launch_monitor_service = LaunchMonitorService()
        shot_config_request = ShotConfigRequest()
        shot_config_request.temperature = self._settings.r10_bluetooth['temperature']
        shot_config_request.humidity = self._settings.r10_bluetooth['humidity']
        shot_config_request.altitude = self._settings.r10_bluetooth['altitude']
        shot_config_request.air_density = self._settings.r10_bluetooth['air_density']
        shot_config_request.tee_range = self._settings.r10_bluetooth['tee_distance']
        launch_monitor_service.shot_config_request.CopyFrom(shot_config_request)
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
        pass
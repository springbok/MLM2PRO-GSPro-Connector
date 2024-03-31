import logging

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyCharacteristic
from PySide6.QtCore import QUuid, QByteArray

from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.mlm2pro_encryption import MLM2PROEncryption


class MLM2PRODevice(BluetoothDeviceBase):
    HEARTBEAT_INTERVAL = 2
    MLM2PRO_HEARTBEAT_INTERVAL = 20

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
        super().__init__(device, MLM2PRODevice.SERVICE_UUID)
        self.user_token = "0"
        self.ball_type = 2
        self.altitude_metres = 0.0
        self.temperature_celsius = 15.0
        self.notification_uuids = [
            MLM2PRODevice.EVENTS_CHARACTERISTIC_UUID,
            MLM2PRODevice.HEARTBEAT_CHARACTERISTIC_UUID,
            MLM2PRODevice.WRITE_RESPONSE_CHARACTERISTIC_UUID,
            MLM2PRODevice.MEASUREMENT_CHARACTERISTIC_UUID
        ]
        self.encryption = MLM2PROEncryption()

    def _authenticate(self):
        print('authenticating')
        if self._is_connected() is False:
            self.error.emit('Device not connected')
            return
        if self.service is None:
            self.error.emit('General service not initialized')
            return
        self.status_update.emit('Authenticating...', self.ble_device.name())
        int_to_byte_array = BluetoothUtils.int_to_byte_array(1, True, False)
        encryption_type_bytes = self.encryption.get_encryption_type_bytes()
        key_bytes = self.encryption.get_key_bytes()
        if key_bytes is None: raise Exception('Key bytes not generated')
        b_arr = bytearray(int_to_byte_array + encryption_type_bytes + key_bytes)
        b_arr[:len(int_to_byte_array)] = int_to_byte_array
        b_arr[len(int_to_byte_array):len(int_to_byte_array) + len(encryption_type_bytes)] = encryption_type_bytes
        start_index = len(int_to_byte_array) + len(encryption_type_bytes)
        end_index = start_index + len(key_bytes)
        b_arr[start_index:end_index] = key_bytes
        self._write_characteristic(MLM2PRODevice.AUTH_CHARACTERISTIC_UUID, b_arr)

    def _data_handler(self, char: QLowEnergyCharacteristic, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'char: {char.uuid().toString()} data: {BluetoothUtils.byte_array_to_hex_string(data.data())}')
        logging.debug(f'received data from {self.ble_device.name()} at {self._sensor_address()}: {BluetoothUtils.byte_array_to_hex_string(data.data())}')

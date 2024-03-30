from PySide6.QtBluetooth import QBluetoothDeviceInfo
from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase


class MLM2PRODevice(BluetoothDeviceBase):
    HEARTBEAT_INTERVAL = 2
    MLM2PRO_HEARTBEAT_INTERVAL = 20

    MLM2PRO_SEND_INITIAL_PARAMS = 2
    MLM2PRO_AUTH_SUCCESS = 0
    MLM2PRO_RAPSODO_AUTH_FAILED = 1
    MLM2PRO_VALID_WRITE_RESPPONSE = 1

    SERVICE_UUID = '{DAF9B2A4-E4DB-4BE4-816D-298A050F25CD}'
    #firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'
    AUTH_CHARACTERISTIC_UUID = '{B1E9CE5B-48C8-4A28-89DD-12FFD779F5E1}'
    COMMAND_CHARACTERISTIC_UUID = "{1EA0FA51-1649-4603-9C5F-59C940323471}"
    CONFIGURE_CHARACTERISTIC_UUID = "{DF5990CF-47FB-4115-8FDD-40061D40AF84}"
    EVENTS_CHARACTERISTIC_UUID = "{02E525FD-7960-4EF0-BFB7-DE0F514518FF}"
    HEARTBEAT_CHARACTERISTIC_UUID = "{EF6A028E-F78B-47A4-B56C-DDA6DAE85CBF}"
    MEASUREMENT_CHARACTERISTIC_UUID = "{76830BCE-B9A7-4F69-AEAA-FD5B9F6B0965}"
    WRITE_RESPONSE_CHARACTERISTIC_UUID  = "{CFBBCB0D-7121-4BC2-BF54-8284166D61F0}"

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

    async def authenticate(self):
        if not self.mlm2pro_client.is_connected:
            raise Exception('Client not connected')
        if self.general_service is None:
            raise Exception('General service not initialized')
        int_to_byte_array = MLM2PROUtils.int_to_byte_array(1, True, False)
        encryption_type_bytes = self.encryption.get_encryption_type_bytes()
        key_bytes = self.encryption.get_key_bytes()
        if key_bytes == None: raise Exception('Key bytes not generated')
        b_arr = bytearray(int_to_byte_array + encryption_type_bytes + key_bytes)
        b_arr[:len(int_to_byte_array)] = int_to_byte_array
        b_arr[len(int_to_byte_array):len(int_to_byte_array) + len(encryption_type_bytes)] = encryption_type_bytes
        start_index = len(int_to_byte_array) + len(encryption_type_bytes)
        end_index = start_index + len(key_bytes)
        b_arr[start_index:end_index] = key_bytes
        print(f'Auth request: {MLM2PROUtils.byte_array_to_hex_string(b_arr)}')
        await self.mlm2pro_client.write_characteristic(self.general_service,
            b_arr,
            MLM2PROAPI.AUTH_CHARACTERISTIC_UUID, True)

import asyncio
import binascii
import json
import logging
import traceback

from bleak import BleakGATTCharacteristic

from src.bluetooth.bluetooth_api_base import BluetoothAPIBase
from src.bluetooth.bluetooth_utils import BluetoothUtils
from src.bluetooth.mlm2pro_device import MLM2PRODevice
from src.bluetooth.mlm2pro_encryption import MLM2PROEncryption
from src.bluetooth.mlm2pro_secret import MLM2PROSecret
from src.bluetooth.mlm2pro_web_api import MLM2PROWebApi


class MLM2PROAPI(BluetoothAPIBase):
    MLM2PRO_HEARTBEAT_INTERVAL = 20

    MLM2PRO_SEND_INITIAL_PARAMS = 2
    MLM2PRO_AUTH_SUCCESS = 0
    MLM2PRO_RAPSODO_AUTH_FAILED = 1
    MLM2PRO_VALID_WRITE_RESPPONSE = 1

    # SERVICE_UUID = '0000180a-0000-1000-8000-00805f9b34fb'
    SERVICE_UUID = 'DAF9B2A4-E4DB-4BE4-816D-298A050F25CD'
    # firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'
    AUTH_CHARACTERISTIC_UUID = 'B1E9CE5B-48C8-4A28-89DD-12FFD779F5E1'
    COMMAND_CHARACTERISTIC_UUID = "1EA0FA51-1649-4603-9C5F-59C940323471"
    CONFIGURE_CHARACTERISTIC_UUID = "DF5990CF-47FB-4115-8FDD-40061D40AF84"
    EVENTS_CHARACTERISTIC_UUID = "02E525FD-7960-4EF0-BFB7-DE0F514518FF"
    HEARTBEAT_CHARACTERISTIC_UUID = "EF6A028E-F78B-47A4-B56C-DDA6DAE85CBF"
    MEASUREMENT_CHARACTERISTIC_UUID = "76830BCE-B9A7-4F69-AEAA-FD5B9F6B0965"
    WRITE_RESPONSE_CHARACTERISTIC_UUID = "CFBBCB0D-7121-4BC2-BF54-8284166D61F0"

    def __init__(self, device: MLM2PRODevice):
        super().__init__(device)
        self.notifications = [
            MLM2PROAPI.EVENTS_CHARACTERISTIC_UUID,
            MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID,
            MLM2PROAPI.WRITE_RESPONSE_CHARACTERISTIC_UUID,
            MLM2PROAPI.MEASUREMENT_CHARACTERISTIC_UUID
        ]
        self.web_api = MLM2PROWebApi(self.settings.web_api['url'], MLM2PROSecret.decrypt(self.settings.web_api['secret']))
        self.encryption = MLM2PROEncryption()

    async def start(self) -> None:
        await super().start()
        print('api start')
        try:
            await self.client.client_connect()
            await self.__setup_device()
        except Exception as e:
            print('def start exception')
            logging.debug(f'Error: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
            raise e

    async def __setup_device(self) -> None:
        print(f'Setting up device: {self.device.ble_device.name} {self.device.ble_device.address}')
        logging.debug(f'Setting up device: {self.device.ble_device.name} {self.device.ble_device.address}')
        self._get_service(MLM2PROAPI.SERVICE_UUID)
        await self._subscribe_to_characteristics()
        self._set_next_expected_heartbeat()
        self._start_heartbeat_task()
        await self.__authenticate()
        print('setup completed')

    async def stop(self) -> None:
        print('xxxxx api stop ')
        await super().stop()
        await self.client.client_disconnect()
        
    async def __authenticate(self) -> None:
        if not self.client.is_connected:
            raise Exception('Client not connected')
        if self.service is None:
            raise Exception('General service not initialized')
        logging.debug('Authenticating...')
        int_to_byte_array = BluetoothUtils.int_to_byte_array(1, True, False)
        encryption_type_bytes = self.encryption.get_encryption_type_bytes()
        key_bytes = self.encryption.get_key_bytes()
        if key_bytes == None: raise Exception('Key bytes not generated')
        b_arr = bytearray(int_to_byte_array + encryption_type_bytes + key_bytes)
        b_arr[:len(int_to_byte_array)] = int_to_byte_array
        b_arr[len(int_to_byte_array):len(int_to_byte_array) + len(encryption_type_bytes)] = encryption_type_bytes
        start_index = len(int_to_byte_array) + len(encryption_type_bytes)
        end_index = start_index + len(key_bytes)
        b_arr[start_index:end_index] = key_bytes
        logging.debug(f'Auth request: {BluetoothUtils.byte_array_to_hex_string(b_arr)}')
        print(f'Auth request: {BluetoothUtils.byte_array_to_hex_string(b_arr)}')
        await self.client.write_characteristic(self.service,
                                                           b_arr,
                                                           MLM2PROAPI.AUTH_CHARACTERISTIC_UUID, True)

    def _notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
        print(f'notification received: {characteristic.description} {binascii.hexlify(data).decode()}')
        if characteristic.uuid.upper() == MLM2PROAPI.WRITE_RESPONSE_CHARACTERISTIC_UUID:
            int_array = BluetoothUtils.bytearray_to_int_array(data)
            print(f'Write response {characteristic.uuid}: {int_array}')
            self.__process_write_response(int_array)
        elif characteristic.uuid.upper() == MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID:
            print(f'Heartbeat received from MLM2PRO {characteristic.uuid}')
            self._set_next_expected_heartbeat()
            

    def __process_write_response(self, data: list[int]) -> None:
        if len(data) >= 2:
            if len(data) > 2:
                if data[0] == MLM2PROAPI.MLM2PRO_SEND_INITIAL_PARAMS:
                    print(f'Auth requested: Initial parameters need to be sent to MLM2PRO {data[0]}')
                    if data[1] != MLM2PROAPI.MLM2PRO_AUTH_SUCCESS or len(data) < 4:
                        print(f'Auth failed: {data[1]}')
                        if data[1] == MLM2PROAPI.MLM2PRO_RAPSODO_AUTH_FAILED:
                            msg = 'Awesome Golf authorisation has expired, please re-authorise in the Rapsodo app and try again once that has been done.'
                            self.error.emit(msg)
                            return
                        else:
                            msg = ('Authentication failed.')
                            logging.debug(msg)
                            self.error.emit(msg)
                            return
                    print('Auth success, send initial params')
                    asyncio.create_task(self.__send_initial_params(data))
            else:
                print('Connected to MLM2PRO, initial parameters not required')

    async def __send_initial_params(self, data) -> None:
        byte_array = data[2:]
        print(f'byte array: {byte_array}')
        byte_array2 = byte_array[:4]
        user_id = BluetoothUtils.bytes_to_int(byte_array2, True)
        print(f'User ID generated from device: {user_id}')
        self.settings.web_api['user_id'] = user_id
        self.settings.save()
        await self.__update_user_token(user_id)
        params = self.device. get_initial_parameters(self.settings.web_api['token'])
        print(f'Initial parameters: {params}')
        await self.__write_command(params)

    async def __update_user_token(self, user_id: int) -> None:
        print(f'updating user token: {user_id}')
        result = self.web_api.send_request(user_id)
        print(f'update user token response: {result}')
        if result is not None:
            response = json.loads(result)
            print('User token updated successfully')
            self.settings.web_api['token'] = response['user']['token']
            self.settings.web_api['token_expiry'] = response['user']['expireDate']
            self.settings.web_api['device_id'] = response['user']['id']
            self.settings.save()
        else:
            print('Failed to update user token')
            raise Exception('Failed to update user token from web API')

    async def _send_heartbeat(self) -> None:
        await self.client.write_characteristic(
            self.service, bytearray([0x01]),
            MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID)


    async def __write_command(self, data):
        if not self.client.is_connected:
            raise Exception('Client not connected')
        if self.service is None:
            raise Exception('General service not initialized')
        print(f'Write config: {BluetoothUtils.byte_array_to_hex_string(data)}')
        await self.client.write_characteristic(self.service,
            self.encryption.encrypt(data),
            MLM2PROAPI.CONFIGURE_CHARACTERISTIC_UUID, True)

    async def write_command(self, data):
        if not self.client.is_connected:
            raise Exception('Client not connected')
        if self.service is None:
            raise Exception('General service not initialized')
        print(f'Write command: {BluetoothUtils.bytearray_to_int_array(data)}')
        await self.client.write_characteristic(self.service,
            self.encryption.encrypt(data),
            MLM2PROAPI.COMMAND_CHARACTERISTIC_UUID, True)

import asyncio
import binascii
import datetime
import json

from bleak import BleakGATTCharacteristic

from src.appdata import AppDataPaths
from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.device import MLM2PRODevice
from src.mlm2pro_bluetooth.encryption import MLM2PROEncryption
from src.mlm2pro_bluetooth.utils import MLM2PROUtils
from src.mlm2pro_bluetooth.web_api import MLM2PROWebApi
from src.settings import Settings


class MLM2PROAPI:
    
    HEARTBEAT_INTERVAL = 2
    MLM2PRO_HEARTBEAT_INTERVAL = 20

    MLM2PRO_SEND_INITIAL_PARAMS = 2
    MLM2PRO_AUTH_SUCCESS = 0
    MLM2PRO_RAPSODO_AUTH_FAILED = 1

    #SERVICE_UUID = '0000180a-0000-1000-8000-00805f9b34fb'
    SERVICE_UUID = 'DAF9B2A4-E4DB-4BE4-816D-298A050F25CD'
    #firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'
    AUTH_CHARACTERISTIC_UUID = 'B1E9CE5B-48C8-4A28-89DD-12FFD779F5E1'
    COMMAND_CHARACTERISTIC_UUID = "1EA0FA51-1649-4603-9C5F-59C940323471"
    CONFIGURE_CHARACTERISTIC_UUID = "DF5990CF-47FB-4115-8FDD-40061D40AF84"
    EVENTS_CHARACTERISTIC_UUID = "02E525FD-7960-4EF0-BFB7-DE0F514518FF"
    HEARTBEAT_CHARACTERISTIC_UUID = "EF6A028E-F78B-47A4-B56C-DDA6DAE85CBF"
    MEASUREMENT_CHARACTERISTIC_UUID = "76830BCE-B9A7-4F69-AEAA-FD5B9F6B0965"
    WRITE_RESPONSE_CHARACTERISTIC_UUID  = "CFBBCB0D-7121-4BC2-BF54-8284166D61F0"


    def __init__(self, client: MLM2PROClient):
        self.mlm2pro_client = client
        self.general_service = None
        self.notifications = [
            MLM2PROAPI.EVENTS_CHARACTERISTIC_UUID,
            MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID,
            MLM2PROAPI.WRITE_RESPONSE_CHARACTERISTIC_UUID,
            MLM2PROAPI.MEASUREMENT_CHARACTERISTIC_UUID
        ]
        self.device = MLM2PRODevice()
        self.started = False
        self.heartbeat_task = None
        self.set_next_expected_heartbeat()
        self.app_paths = AppDataPaths('mlm2pro-gspro-connect')
        self.settings = Settings(self.app_paths)
        print(f'settings: {self.settings.to_json()}')
        self.web_api = MLM2PROWebApi(self.settings.web_api['url'], self.settings.web_api['secret'])
        self.encryption = MLM2PROEncryption()


    async def stop(self):
        print('api stop')
        if self.started:
            self.started = False
            self.stop_heartbeat_task()

    async def start(self):
        if not self.mlm2pro_client.is_connected:
            raise Exception('Client not connected')
        print('api start')
        self.general_service = self.mlm2pro_client.bleak_client.services.get_service(MLM2PROAPI.SERVICE_UUID)
        if self.general_service is None:
            raise Exception('General service not found')
        await self.subscribe_to_characteristics()
        self.set_next_expected_heartbeat()
        self.start_heartbeat_task()
        self.started = True
        print('init completed')

    async def read_firmware_version(self):
        if self.general_service is None:
            raise Exception('General service not initialized')
        characteristic = self.general_service.get_characteristic(MLM2PROAPI.firmware_characteristic_uuid)
        if characteristic is None or not "read" in characteristic.properties:
            raise Exception('Firmware characteristic not found or not readable')
        value = await self.mlm2pro_client.bleak_client.read_gatt_char(characteristic.uuid)
        return value

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        print(f'notification received: {characteristic.description} {binascii.hexlify(data).decode()}')
        if characteristic.uuid.upper() == MLM2PROAPI.WRITE_RESPONSE_CHARACTERISTIC_UUID:
            int_array = MLM2PROUtils.bytearray_to_int_array(data)
            print(f'Write response {characteristic.uuid}: {int_array}')
            self.__process_write_response(int_array)
        elif characteristic.uuid.upper() == MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID:
            print(f'Heartbeat received from MLM2PRO {characteristic.uuid}')
            self.set_next_expected_heartbeat()

    def __process_write_response(self, data: list[int]):
        if len(data) >= 2:
            if len(data) > 2:
                if data[0] == MLM2PROAPI.MLM2PRO_SEND_INITIAL_PARAMS:
                    print(f'Auth requested: Initial parameters need to be sent to MLM2PRO {data[0]}')
                    if data[1] != MLM2PROAPI.MLM2PRO_AUTH_SUCCESS or len(data) < 4:
                        print(f'Auth failed: {data[1]}')
                        if data[1] == MLM2PROAPI.MLM2PRO_RAPSODO_AUTH_FAILED:
                            raise Exception('Awesome Golf authorisation has expired, please re-authorise in the Rapsodo app and try again once that has been done.')
                        else:
                            raise Exception('Auth failed')
                    print('Auth success, send initial params')
                    byte_array = data[2:]
                    print(f'byte array: {byte_array}')
                    byte_array2 = byte_array[:4]
                    user_id = MLM2PROUtils.bytes_to_int(byte_array2, True)
                    print(f'User ID generated from device: {user_id}')
                    self.settings.web_api['user_id'] = user_id
                    self.settings.save()
                    asyncio.create_task(self.update_user_token(user_id))
            else:
                print('Connected to MLM2PRO, initial parameters not required')

    async def heartbeat(self):
        while self:
            print('heartbeat')
            if self.mlm2pro_client.is_connected:
                print(f'writing heartbeat {datetime.datetime.utcnow()} self.next_heartbeat: {self.next_heartbeat}')
                if datetime.datetime.utcnow() > self.next_heartbeat:
                    # heartbeat not received within 20 seconds, reset subscriptions
                    print('Heartbeat not received for 20 seconds, resubscribing...')
                    self.set_next_expected_heartbeat()
                    await self.subscribe_to_characteristics()
                await self.mlm2pro_client.write_characteristic(self.general_service, bytearray([0x01]), MLM2PROAPI.HEARTBEAT_CHARACTERISTIC_UUID)
            await asyncio.sleep(MLM2PROAPI.HEARTBEAT_INTERVAL)

    def start_heartbeat_task(self):
        if self.heartbeat_task is None or self.heartbeat_task.done() or \
            self.heartbeat_task.cancelled() and self.mlm2pro_client.is_connected:
            self.heartbeat_task = asyncio.create_task(self.heartbeat())
            self.set_next_expected_heartbeat()
            print('heartbeat task created')

    def stop_heartbeat_task(self):
        if self.heartbeat_task is not None and not self.heartbeat_task.done() and \
            not self.heartbeat_task.cancelled():
            self.heartbeat_task.cancel()
            print('heartbeat task cancelled')

    def set_next_expected_heartbeat(self):
        now = datetime.datetime.utcnow()
        self.next_heartbeat = now + datetime.timedelta(seconds=MLM2PROAPI.MLM2PRO_HEARTBEAT_INTERVAL)
        print(f'next heartbeat expected at {self.next_heartbeat} now: {now}')

    async def subscribe_to_characteristics(self):
        for i in range(3):
            try:
                await self.mlm2pro_client.subscribe_to_characteristics(self.notifications,
                                                                       self.notification_handler)
                print('subscribed to characteristics')
                break
            except Exception as e:
                if i == 2:
                    raise Exception('Error while connecting WindowsError: {e}')
                else:
                    await asyncio.sleep(1)
                    print(f'Error while connecting WindowsError: {e}')
                    await self.mlm2pro_client.stop()
                    await self.mlm2pro_client.start()

    async def auth(self):
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

    async def __write_config(self, data):
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

    async def send_(self, data):

    async def update_user_token(self, user_id: str):
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
            params = self.device.get_initial_parameters(response['user']['token'])
            print(f'Initial parameters: {params}')
        else:
            print('Failed to update user token')
            raise Exception('Failed to update user token from web API')
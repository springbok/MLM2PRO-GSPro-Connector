import asyncio
import binascii

from bleak import BleakGATTCharacteristic

from src.mlm2pro_bluetooth.client import MLM2PROClient
from src.mlm2pro_bluetooth.utils import MLM2PROUtils


class MLM2PROAPI:
    
    HEARTBEAT_INTERVAL = 2

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
        self.started = False
        self.heartbeat_task = None

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
        await self.mlm2pro_client.subscribe_to_characteristics(self.notifications, self.notification_handler)
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

    async def auth(self):
        if not self.mlm2pro_client.is_connected:
            raise Exception('Client not connected')
        if self.general_service is None:
            raise Exception('General service not initialized')
        await self.mlm2pro_client.write_characteristic(self.general_service,
            bytearray.fromhex('0100000000011A180126F99A3C3F95B9CD967EA0263D59C7448CFF15FA8337A579FA3179E915'),
            MLM2PROAPI.AUTH_CHARACTERISTIC_UUID, True)
        print('write auth')

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        print(f'notification received: {characteristic.description} {binascii.hexlify(data).decode()}')
        if characteristic.uuid.upper() == MLM2PROAPI.WRITE_RESPONSE_CHARACTERISTIC_UUID:
            print(f'write response {characteristic.uuid}')
            int_array = MLM2PROUtils.bytearray_to_int_array(data)
            print(f'int_array:  {int_array}')

    async def heartbeat(self):
        while self:
            print('heartbeat')
            await asyncio.sleep(MLM2PROAPI.HEARTBEAT_INTERVAL)

    def start_heartbeat_task(self):
        if self.heartbeat_task is None or self.heartbeat_task.done() or \
            self.heartbeat_task.cancelled() and self.mlm2pro_client.is_connected:
            self.heartbeat_task = asyncio.create_task(self.heartbeat())
            print('heartbeat task created')

    def stop_heartbeat_task(self):
        if self.heartbeat_task is not None and not self.heartbeat_task.done() and \
            not self.heartbeat_task.cancelled():
            self.heartbeat_task.cancel()
            print('heartbeat task cancelled')

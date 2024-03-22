import binascii

from bleak import BleakGATTCharacteristic

from src.mlm2pro_bluetooth.client import MLM2PROClient


class MLM2PROAPI:

    #service_uuid = '0000180a-0000-1000-8000-00805f9b34fb'
    service_uuid = 'DAF9B2A4-E4DB-4BE4-816D-298A050F25CD'
    #firmware_characteristic_uuid = '00002a29-0000-1000-8000-00805f9b34fb'
    auth_characteristic_uuid = 'B1E9CE5B-48C8-4A28-89DD-12FFD779F5E1'
    command_characteristic_uuid = "1EA0FA51-1649-4603-9C5F-59C940323471"
    configure_characteristic_uuid = "DF5990CF-47FB-4115-8FDD-40061D40AF84"
    events_characteristic_uuid = "02E525FD-7960-4EF0-BFB7-DE0F514518FF"
    heartbeat_characteristic_uuid = "EF6A028E-F78B-47A4-B56C-DDA6DAE85CBF"
    measurement_characteristic_uuid = "76830BCE-B9A7-4F69-AEAA-FD5B9F6B0965"
    write_responseCharacteristic_uuid  = "CFBBCB0D-7121-4BC2-BF54-8284166D61F0"


    def __init__(self, client: MLM2PROClient):
        self.mlm2pro_client = client
        self.general_service = None
        self.notifications = [
            MLM2PROAPI.events_characteristic_uuid,
            MLM2PROAPI.heartbeat_characteristic_uuid,
            MLM2PROAPI.write_responseCharacteristic_uuid,
            MLM2PROAPI.measurement_characteristic_uuid
        ]
        self.started = False

    async def stop(self):
        print('api stop')
        if self.started:
            await self.mlm2pro_client.unsubscribe_to_characteristics()
            self.started = False

    async def start(self):
        print('api start')
        self.general_service = self.mlm2pro_client.bleak_client.services.get_service(MLM2PROAPI.service_uuid)
        if self.general_service is None:
            raise Exception('General service not found')
        await self.mlm2pro_client.subscribe_to_characteristics(self.notifications, self.notification_handler)
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
        if self.general_service is None:
            raise Exception('General service not initialized')
        await self.mlm2pro_client.write_characteristic(self.general_service,
            bytearray.fromhex('0100000000011A180126F99A3C3F95B9CD967EA0263D59C7448CFF15FA8337A579FA3179E915'),
            MLM2PROAPI.auth_characteristic_uuid, True)
        print('write auth')

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        """Simple notification handler which prints the data received."""
        print(f'notification received: {characteristic.description} {binascii.hexlify(data).decode()}')
        int_array = [byte & 0xFF for byte in data]
        print(f'int_array:  {int_array}')

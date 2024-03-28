import logging

from src.bluetooth.bluetooth_api_base import BluetoothAPIBase
from src.bluetooth.mlm2pro_device import MLM2PRODevice


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

    async def start(self):
        print('api start')
        await self.client.client_connect()
        await self.__setup_device()

    async def __setup_device(self):
        print(f'Setting up device: {self.device.ble_device.name} {self.device.ble_device.address}')
        logging.debug(f'Setting up device: {self.device.ble_device.name} {self.device.ble_device.address}')
        logging.debug(f'Setting up service: {MLM2PROAPI.SERVICE_UUID}')
        await self._get_service(MLM2PROAPI.SERVICE_UUID)
        if self.service is None:
            raise Exception(f'Service {MLM2PROAPI.SERVICE_UUID} not found')
        #await self.subscribe_to_characteristics()
        #self.set_next_expected_heartbeat()
        #self.start_heartbeat_task()
        #self.started = True
        print('setup completed')
        #if self.client.is_connected:
        #    result = await self.__authenticate()

    async def stop(self):
        await self.client.client_disconnect()

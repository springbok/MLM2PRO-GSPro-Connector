import asyncio
import datetime
import logging

from PySide6.QtCore import QObject, Signal
from bleak import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService

from src.appdata import AppDataPaths
from src.bluetooth.bluetooth_client import BluetoothClient
from src.settings import Settings


class BluetoothAPIBase(QObject):
    HEARTBEAT_INTERVAL = 2

    error = Signal(str)

    def __init__(self, device) -> None:
        super().__init__()
        self.device = device
        print(f'BluetoothAPIBase {device}')
        self.client = BluetoothClient(device)
        self.notifications = []
        self.heartbeat_task = None
        self._set_next_expected_heartbeat()
        self.service = None
        self.app_paths = AppDataPaths('mlm2pro-gspro-connect')
        self.settings = Settings(self.app_paths)
        print(f'settings: {self.settings.to_json()}')

    async def start(self):
        pass

    async def stop(self):
        print('stop heartbeat')
        self._stop_heartbeat_task()
        print('unsibscribing')
        await self.client.unsubscribe_to_characteristics()

    def _stop_heartbeat_task(self) -> None:
        if self.heartbeat_task is not None and not self.heartbeat_task.done() and not self.heartbeat_task.cancelled():
            print('stopping heartbeat task')
            self.heartbeat_task.cancel()

    def _get_service(self, uuid: str) -> BleakGATTService:
        self.service = self.client.get_service(uuid)
        return self.service

    async def _subscribe_to_characteristics(self) -> None:
        for i in range(3):
            try:
                await self.client.subscribe_to_characteristics(self.notifications, self._notification_handler)
                break
            except Exception as e:
                if i == 2:
                    await self.client.client_disconnect()
                    raise Exception(f'Error while connecting WindowsError: {e}')
                else:
                    await asyncio.sleep(1)
                    logging.debug(f'Error while connecting WindowsError: {e}')
                    await self.client.client_disconnect()
                    await self.client.client_connect()


    def _notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
        pass

    def _set_next_expected_heartbeat(self) -> None:
        now = datetime.datetime.utcnow()
        self.next_heartbeat = now + datetime.timedelta(seconds=BluetoothAPIBase.HEARTBEAT_INTERVAL)
        print(f'next heartbeat expected at {self.next_heartbeat} now: {now}')

    def _start_heartbeat_task(self) -> None:
        if self.heartbeat_task is None or self.heartbeat_task.done() or \
            self.heartbeat_task.cancelled() and self.client.is_connected:
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
            self._set_next_expected_heartbeat()
            print('heartbeat task created')

    async def _heartbeat(self):
        while self:
            print('heartbeat')
            if self.client.is_connected:
                print(f'writing heartbeat {datetime.datetime.utcnow()} self.next_heartbeat: {self.next_heartbeat}')
                if datetime.datetime.utcnow() > self.next_heartbeat:
                    # heartbeat not received within 20 seconds, reset subscriptions
                    print('Heartbeat not received for 20 seconds, resubscribing...')
                    logging.debug('Heartbeat not received for 20 seconds, resubscribing...')
                    self._set_next_expected_heartbeat()
                    await self._subscribe_to_characteristics()
                await self._send_heartbeat()
            await asyncio.sleep(BluetoothAPIBase.HEARTBEAT_INTERVAL)

    async def _send_heartbeat(self) -> None:
        pass
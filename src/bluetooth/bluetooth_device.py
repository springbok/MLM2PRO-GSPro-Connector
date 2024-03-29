import asyncio
import logging
import traceback

from PySide6.QtCore import QObject, Signal
from bleak import BLEDevice, AdvertisementData, BleakClient

from src.bluetooth.bluetooth_signal import BluetoothSignal


class BluetoothDevice(QObject):
    """
    Connect to a device that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    the app. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """
    device_error = Signal(str, str)
    device_connecting = Signal(BluetoothSignal)
    device_disconnected = Signal()
    device_disconnecting = Signal(BluetoothSignal)
    device_connected = Signal(BluetoothSignal)
    device_setting_up = Signal(BluetoothSignal)

    def __init__(self, device: BLEDevice, advertised_data: AdvertisementData) -> None:
        super().__init__()
        self.ble_device = device
        self.advertised_data = advertised_data
        self.disconnection_request = asyncio.Event()
        self.device_lock = asyncio.Lock()

    def stop(self):
        self.__disconnect_from_device()

    def __disconnect_from_device(self):    # regular subroutines are called from main (GUI) thread with `call_soon_threadsafe`
        """Disconnect from current BLE server."""
        if not self.device_lock.locked():    # early return if no sensor is connected
            logging.debug("Disconnect device: currently there is no device connected.")
        else:
            logging.debug(f"Disconnecting from device: {self.ble_device.name}")
            self.device_disconnecting.emit(BluetoothSignal('Disconnecting...', 'orange', self.ble_device, 'red', 'Stop', False))
        self.disconnection_request.set()
        self.disconnection_request.clear()

    async def connect_device(self, address) -> None:    # async methods are called from the main (GUI) thread with `run_coroutine_threadsafe`
        """Connect to BLE server at address."""
        if self.device_lock.locked():    # don't allow new connection while current client is (dis-)connecting or connected
            msg = f"Device {self.ble_device.name} is already connected."
            logging.debug(msg)
        else:
            async with self.device_lock:    # device_lock context exits and releases lock once client is disconnected, either through regular disconnection or failed connection attempt
                logging.debug(
                    f'Attempting to connect to device: {self.ble_device.name} {self.ble_device.address}')
                self.device_connecting.emit(BluetoothSignal('Connecting...', 'orange', self.ble_device, 'red', 'Stop', False))
                async with BleakClient(address, disconnected_callback=self.__reconnect_client) as client:    # __aenter__() calls client.connect() and raises if connection attempt fails
                    try:
                        logging.debug(f'Setting up & configuring device {self.ble_device.name}')
                        self.device_setting_up.emit(BluetoothSignal('Setting up device...', 'orange', self.ble_device, 'red', 'Stop', False))
                        await self._setup_device()
                        logging.debug(f'Device connected {self.ble_device.name}')
                        self.device_connected.emit(BluetoothSignal('Connected', 'green', self.ble_device, 'red', 'Stop', True))
                        await self.disconnection_request.wait()    # block until `disconnection_request` is set
                        client.set_disconnected_callback(None)
                    except Exception as e:
                        logging.debug(f'Error: {format(e)}, {traceback.format_exc()}')
                        self.device_error.emit('Unexpected error', traceback.format_exc())
                        self.__disconnect_from_device()
                        raise e
            self.device_disconnected.emit()
            logging.debug(f"Disconnected from device: {self.ble_device.name}")

    async def _setup_device(self) -> None:
        pass

    def __reconnect_client(self, client) -> None:
        """Handle unexpected disconnection."""
        logging.debug(f"Lost connection to device {self.ble_device.name} at {client.address}")
        asyncio.get_event_loop().call_soon(self.__disconnect_from_device)

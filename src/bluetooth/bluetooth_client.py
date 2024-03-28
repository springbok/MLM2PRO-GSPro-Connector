import asyncio
import logging
import traceback

from PySide6.QtCore import QObject, QByteArray, Signal
from bleak import BLEDevice, BleakClient

from src.bluetooth.bluetooth_device import BluetoothDevice


class BluetoothClient(QObject):
    """
    Connect to a device that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    the app. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """

    client_error = Signal(str)
    client_connecting = Signal(str)
    client_disconnected = Signal(str)
    client_disconnecting = Signal(str)
    client_connected = Signal(str)

    def __init__(
        self,
        device: BluetoothDevice,
        connect_timeout: float = 10
    ) -> None:
        super().__init__()
        if device is None:
            raise Exception("Device is None")
        self.bleak_client = BleakClient(device.ble_device, timeout=connect_timeout, disconnected_callback=self.__disconnected)
        self.device = device
        self.connect_timeout = connect_timeout
        self.subscriptions = []
        self.started = False

    @property
    def is_connected(self) -> bool:
        return self.bleak_client.is_connected

    def __disconnected(self, client: BleakClient):
        self.client_disconnected.emit(self.device.ble_device.name)
        logging.debug(f'Disconnected from device: {self.device.ble_device.name} {self.device.ble_device.address}')

    async def client_connect(self) -> None:
        print('bluetooth_client connect')
        if not self.is_connected:
            logging.debug(f'Attempting to connect to device: {self.device.ble_device.name} {self.device.ble_device.address}')
            self.client_connecting.emit(self.device.ble_device.name)
            for i in range(3):
                try:
                    print('bleak connect')
                    await self.bleak_client.connect()
                    print(f'connected self.bleak_client.is_connected {self.bleak_client.is_connected}')
                    self.client_connected.emit(self.device.ble_device.name)
                    break
                except WindowsError as e:
                    logging.debug(f'Error while connecting WindowsError: {e}')
                    await asyncio.sleep(1)
                except Exception as e:
                    logging.debug(f'Error: {format(e)}, {traceback.format_exc()}')
                    print(f'Error: {format(e)}, {traceback.format_exc()}')
                    raise e


    async def client_disconnect(self) -> None:
        print(f'disconnect {self.bleak_client.is_connected}')
        if self.is_connected:
            print('disconnecting')
            logging.debug(f'Disconnecting from device: {self.device.ble_device.name} {self.device.ble_device.address}')
            #await self.bleak_client.unpair()
            self.client_disconnecting.emit(self.device.ble_device.name)
            await self.bleak_client.disconnect()  # type: ignore

'''

    def connect_client(self, device: QBluetoothDeviceInfo):
        print(f'connect_client {device.name()}')
        if self.client is not None:
            logging.debug(f"Currently connected to {self.device.ble_device.name()} at {self.device.ble_device.remoteAddress().toString()}.")
            self.status_update.emit('Connected')
            return
        print(f'Connecting to {device.name()}')
        self.device.ble_device = device
        self.status_update.emit('Connecting...')
        self.client = QLowEnergyController.createCentral(self.device.ble_device)
        self.client.setRemoteAddressType(QLowEnergyController.RemoteAddressType.PublicAddress)
        self.client.errorOccurred.connect(self.catch_error)
        self.client.connected.connect(self.discover_services)
        self.client.serviceDiscovered.connect(self.service_found)
        #self.client.discoveryFinished.connect(self.connect_to_service)
        self.client.disconnected.connect(self.reset_connection)
        print('bef connect')
        self.client.connectToDevice()
        print('aft connect')

    def service_found(self, service_uuid: QBluetoothUuid):
        print(f'service_found {service_uuid}')
        service = self.client.createServiceObject(service_uuid)
        if not service:
            raise Exception("Cannot create service from uuid")
            return

        serv = ServiceInfo(service)
        print(f'service_found {service.serviceUuid().toString()} {serv.service_uuid}')


    def disconnect_client(self):
        if self.hr_notification is not None and self.service is not None:
            if not self.hr_notification.isValid():
                return
            print("Unsubscribing from HR service.")
            self.service.writeDescriptor(
                self.hr_notification, self.DISABLE_NOTIFICATION
            )
        if self.client is not None:
            self.status_update.emit('Disconnecting...')
            self.client.disconnectFromDevice()

    def discover_services(self):
        print('discover services')
        if self.client is not None:
            logging.debug(f'Discovering services for {self.device.ble_device.name()}')
            self.status_update.emit('Discovering services...')
            self.client.discoverServices()

    def connect_to_service(self):
        print('connect_to_service')
        if self.client is None:
            return
        print(f'connect_to_service {self.device.ble_device.name()}')
        for s in self.client.services():
            service = self.controller.createServiceObject(service_uuid)
            serv = ServiceInfo(s)
            print(f'service: {serv.service_uuid()}')
        return
        hr_service: list[QBluetoothUuid] = [
            s for s in self.client.services() if s == self.service
        ]
        if not hr_service:
            print(f"Couldn't find HR service on {self.device.ble_device.remoteAddress().toString()}.")
            return
        self.service = self.client.createServiceObject(hr_service[0])
        if not self.service:
            print(
                f"Couldn't establish connection to HR service on {self.device.ble_device.remoteAddress().toString()}."
            )
            return
        self.service.stateChanged.connect(self._start_hr_notification)
        self.service.characteristicChanged.connect(self.data_handler)
        self.service.discoverDetails()

    def _start_hr_notification(self, state: QLowEnergyService.ServiceState):
        if state != QLowEnergyService.RemoteServiceDiscovered:
            return
        if self.service is None:
            return
        hr_char: QLowEnergyCharacteristic = self.service.characteristic(
            self.HR_CHARACTERISTIC
        )
        if not hr_char.isValid():
            print(f"Couldn't find HR characterictic on {self.device.ble_device.remoteAddress().toString()}.")
        self.hr_notification = hr_char.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.hr_notification.isValid():
            print("HR characteristic is invalid.")
        self.service.writeDescriptor(self.hr_notification, self.ENABLE_NOTIFICATION)

    def reset_connection(self):
        print('disconnected')
        self.client_disconnected.emit()
        logging.debug(f"Discarding connection.")
        self._remove_service()
        self._remove_client()

    def _remove_service(self):
        if self.service is None:
            return
        try:
            self.service.deleteLater()
        except Exception as e:
            print(f"Couldn't remove service: {e}")
        finally:
            self.service = None
            self.hr_notification = None

    def _remove_client(self):
        if self.client is None:
            return
        try:
            self.client.disconnected.disconnect()
            self.client.deleteLater()
        except Exception as e:
            print(f"Couldn't remove client: {e}")
        finally:
            self.client = None

    def catch_error(self, error):
        print(f'error: {error}')
        self.error.emit(f"An error occurred: {error}. Disconnecting device.")
        self.reset_connection()

    def data_handler(self, _, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'received data from {self.device.ble_device.name()} at {self.device.ble_device.remoteAddress().toString()}: {data.toStdString()}')
        
'''
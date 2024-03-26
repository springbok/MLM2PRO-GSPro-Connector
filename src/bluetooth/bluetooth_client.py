import logging

from PySide6.QtBluetooth import QLowEnergyController, QLowEnergyService, QBluetoothDeviceInfo, QLowEnergyCharacteristic, \
    QBluetoothUuid
from PySide6.QtCore import QObject, QByteArray, Signal
from typing import Union


class BluetoothClient(QObject):
    """
    Connect to a device that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    the app. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """

    #ibi_update = Signal(object)
    status_update = Signal(str)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.device = None
        self.client: Union[None, QLowEnergyController] = None
        self.service: Union[None, QLowEnergyService] = None
        #self.hr_notification: Union[None, QLowEnergyDescriptor] = None
        #self.ENABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0100")
        #self.DISABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0000")
        #self.service: QBluetoothUuid.ServiceClassUuid = (
        #    QBluetoothUuid.ServiceClassUuid.HeartRate
        #)
        #self.HR_CHARACTERISTIC: QBluetoothUuid.CharacteristicType = (
        #    QBluetoothUuid.CharacteristicType.HeartRateMeasurement
        #)

    #def _sensor_address(self):
    #    return get_sensor_remote_address(self.client)

    def connect_client(self, device: QBluetoothDeviceInfo):
        if self.client is not None:
            logging.debug(f"Currently connected to {self.device.name()} at {self.device.remoteAddress().toString()}.")
            self.status_update.emit('Connected')
            return
        self.device = device
        self.status_update.emit('Connecting...')
        self.client = QLowEnergyController.createCentral(self.device)
        self.client.errorOccurred.connect(self.___catch_error)
        self.client.connected.connect(self.__discover_services)
        self.client.discoveryFinished.connect(self.__connect_to_service)
        self.client.disconnected.connect(self.__reset_connection)
        self.client.connectToDevice()

    def disconnect_client(self):
        if self.hr_notification is not None and self.service is not None:
            if not self.hr_notification.isValid():
                return
            print("Unsubscribing from HR service.")
            self.service.writeDescriptor(
                self.hr_notification, self.DISABLE_NOTIFICATION
            )
        if self.client is not None:
            self.status_update.emit(
                f"Disconnecting from sensor at {self.device.remoteAddress().toString()}."
            )
            self.client.disconnectFromDevice()

    def __discover_services(self):
        if self.client is not None:
            logging.debug(f'Discovering services for {self.device.name()}')
            self.status_update.emit('Discovering services...')
            self.client.discoverServices()

    def __connect_to_service(self):
        if self.client is None:
            return
        print(f'__connect_to_service {self.device.name()}')
        for s in self.client.services():
            print(f'service: {s.serviceClassToString()}')
            for c in s.characteristics():
                print(f'characteristic: {c.uuid().toString()}')
        return
        hr_service: list[QBluetoothUuid] = [
            s for s in self.client.services() if s == self.service
        ]
        if not hr_service:
            print(f"Couldn't find HR service on {self.device.remoteAddress().toString()}.")
            return
        self.service = self.client.createServiceObject(hr_service[0])
        if not self.service:
            print(
                f"Couldn't establish connection to HR service on {self.device.remoteAddress().toString()}."
            )
            return
        self.service.stateChanged.connect(self._start_hr_notification)
        self.service.characteristicChanged.connect(self._data_handler)
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
            print(f"Couldn't find HR characterictic on {self.device.remoteAddress().toString()}.")
        self.hr_notification = hr_char.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.hr_notification.isValid():
            print("HR characteristic is invalid.")
        self.service.writeDescriptor(self.hr_notification, self.ENABLE_NOTIFICATION)

    def __reset_connection(self):
        logging.debug(f"Discarding {self.device.name()} at {self.device.remoteAddress().toString()}.")
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

    def ___catch_error(self, error):
        self.error.emit(f"An error occurred: {error}. Disconnecting device.")
        self.__reset_connection()

    def _data_handler(self, _, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'received data from {self.device.name()} at {self.device.remoteAddress().toString()}: {data.toStdString()}')
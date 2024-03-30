import logging

from PySide6.QtBluetooth import QLowEnergyController, QLowEnergyService, QBluetoothDeviceInfo, QLowEnergyCharacteristic, \
    QBluetoothUuid
from PySide6.QtCore import QObject, QByteArray, Signal
from typing import Union

from src.bluetooth.service_info import ServiceInfo


class BluetoothDeviceBase(QObject):
    """
    Connect to a device that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    the app. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """

    error = Signal(str)
    disconnecting = Signal(str)
    disconnected = Signal(str)
    connecting = Signal(str)
    connected = Signal(str)
    status_update = Signal(str, str)

    def __init__(self, device: QBluetoothDeviceInfo):
        super().__init__()
        self.device = device
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

    def connect_device(self):
        if self.device is None:
            raise Exception("No device to connect to.")
        print(f'connect_client {self.device.name()}')
        if self.client is not None:
            logging.debug(f"Currently connected to {self.device.name()} at {self.device.remoteAddress().toString()}.")
            self.connected.emit('Connected')
            return
        print(f'Connecting to {self.device.name()}')
        self.status_update.emit('Connecting...', self.device.name())
        self.client = QLowEnergyController.createCentral(self.device)
        self.client.setRemoteAddressType(QLowEnergyController.RemoteAddressType.PublicAddress)
        self.client.errorOccurred.connect(self.__catch_error)
        self.client.connected.connect(self.__discover_services)
        self.client.serviceDiscovered.connect(self.__service_found)
        #self.client.discoveryFinished.connect(self.connect_to_service)
        self.client.disconnected.connect(self.__reset_connection)
        self.client.connectToDevice()

    def __service_found(self, service_uuid: QBluetoothUuid):
        print(f'__service_found {service_uuid}')
        service = self.client.createServiceObject(service_uuid)
        if not service:
            raise Exception("Cannot create service from uuid")
            return

        print(f'__service_found {service.serviceUuid().toString()} {service_uuid.toString()}')


    def disconnect_device(self):
        '''
        if self.hr_notification is not None and self.service is not None:
            if not self.hr_notification.isValid():
                return
            print("Unsubscribing from HR service.")
            self.service.writeDescriptor(
                self.hr_notification, self.DISABLE_NOTIFICATION
            )
        '''
        if self.device is not None:
            logging.debug(f'Disconnecting from device: {self.device.name()}')
        if self.client is not None:
            self.disconnecting.emit('Disconnecting...')
            self.client.disconnectFromDevice()


    def __discover_services(self):
        print('discover services')
        if self.client is not None:
            logging.debug(f'Discovering services for {self.device.name()}')
            self.status_update.emit('Discovering services...', self.device.name())
            self.client.discoverServices()

    def connect_to_service(self):
        print('connect_to_service')
        if self.client is None:
            return
        print(f'connect_to_service {self.device.name()}')
        for s in self.client.services():
            service = self.controller.createServiceObject(service_uuid)
            serv = ServiceInfo(s)
            print(f'service: {serv.service_uuid()}')
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
            print(f"Couldn't find HR characterictic on {self.device.remoteAddress().toString()}.")
        self.hr_notification = hr_char.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.hr_notification.isValid():
            print("HR characteristic is invalid.")
        self.service.writeDescriptor(self.hr_notification, self.ENABLE_NOTIFICATION)

    def __reset_connection(self) -> None:
        self.disconnected.emit('Disconnected')
        logging.debug(f"Disconnected from device, cleaning up")
        self.__remove_service()
        self.__remove_client()
        self.device = None

    def __remove_service(self) -> None:
        if self.service is None:
            return
        try:
            logging.debug('Deleting bluetooth service')
            self.service.deleteLater()
        except Exception as e:
            logging.debug(f"Couldn't remove service: {e}")
        finally:
            self.service = None
            #self.hr_notification = None

    def __remove_client(self) -> None:
        if self.client is None:
            return
        try:
            logging.debug('Deleting bluetooth client')
            self.client.disconnected.disconnect()
            self.client.deleteLater()
        except Exception as e:
            print(f"Couldn't remove client: {e}")
        finally:
            self.client = None

    def __catch_error(self, error) -> None:
        if error == QLowEnergyController.Error.ConnectionError:
            msg = f'Make sure the device is turned on and in range.'
        elif error == QLowEnergyController.Error.AuthorizationError:
            msg = f'The device is not authorized to connect to the device.'
        else:
            msg = f'An unknown error has occurred.'
        if self.client is not None:
            msg = f'{self.client.errorString()} {msg}'
        logging.debug(msg)
        self.error.emit(msg)
        self.__reset_connection()

    def data_handler(self, _, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'received data from {self.device.name()} at {self.device.remoteAddress().toString()}: {data.toStdString()}')
import logging

from PySide6.QtBluetooth import QLowEnergyController, QLowEnergyService, QBluetoothDeviceInfo, QLowEnergyCharacteristic, \
    QBluetoothUuid
from PySide6.QtCore import QObject, QByteArray, Signal, QUuid
from typing import Union

from src.bluetooth.bluetooth_utils import BluetoothUtils
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
    rssi_read = Signal(int)

    def __init__(self, device: QBluetoothDeviceInfo, service_uuid: str):
        super().__init__()
        self.ble_device = device
        self.client: Union[None, QLowEnergyController] = None
        self.service: Union[None, QLowEnergyService] = None
        self.service_uuid = QBluetoothUuid(QUuid(service_uuid))
        self.notification_uuids = []
        self.notifications = []
        self.ENABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0100")
        self.DISABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0000")

        #self.hr_notification: Union[None, QLowEnergyDescriptor] = None
        #self.service: QBluetoothUuid.ServiceClassUuid = (
        #    QBluetoothUuid.ServiceClassUuid.HeartRate
        #)
        #self.HR_CHARACTERISTIC: QBluetoothUuid.CharacteristicType = (
        #    QBluetoothUuid.CharacteristicType.HeartRateMeasurement
        #)

    def __sensor_address(self):
        return self.client.remoteAddress().toString()

    def connect_device(self):
        if self.ble_device is None:
            raise Exception("No device to connect to.")
        print(f'connect_client {self.ble_device.name()}')
        if self.client is not None:
            logging.debug(f"Currently connected to {self.ble_device.name()} at {self.ble_device.remoteAddress().toString()}.")
            self.connected.emit('Connected')
            return
        print(f'Connecting to {self.ble_device.name()}')
        self.status_update.emit('Connecting...', self.ble_device.name())
        self.client = QLowEnergyController.createCentral(self.ble_device)
        self.client.setRemoteAddressType(QLowEnergyController.RemoteAddressType.PublicAddress)
        self.client.errorOccurred.connect(self.__catch_error)
        self.client.connected.connect(self.__discover_services)
        self.client.rssiRead.connect(self.__rssi_read)
        self.client.serviceDiscovered.connect(self.__service_found)
        self.client.discoveryFinished.connect(self.__connect_to_service)
        self.client.disconnected.connect(self.__reset_connection)
        #self.client.rssiRead.connect(self.__rssi_read)
        self.client.connectToDevice()

    def __rssi_read(self, rssi: int):
        self.rssi_read.emit(rssi)

    def __service_found(self, service_uuid: QBluetoothUuid):
        logging.debug(f'Found service: {service_uuid.toString()}')
        print(f'Found service: {service_uuid.toString()}')


    def disconnect_device(self):
        print(f'self.notifications: {self.notifications}')
        if len(self.notifications) > 0 and self.service is not None:
            logging.debug('Unsubscribing from notifications')
            print('Unsubscribing from notifications')
            for notification in self.notifications:
                if not notification.isValid():
                    self.service.writeDescriptor(notification, self.DISABLE_NOTIFICATION)
        if self.ble_device is not None:
            logging.debug(f'Disconnecting from device: {self.ble_device.name()}')
        if self.client is not None:
            self.disconnecting.emit('Disconnecting...')
            self.client.disconnectFromDevice()


    def __discover_services(self):
        print('discover services')
        if self.client is not None:
            logging.debug(f'Discovering services for {self.ble_device.name()}')
            self.status_update.emit('Discovering services...', self.ble_device.name())
            self.client.discoverServices()

    def __connect_to_service(self):
        self.status_update.emit('Connecting to service...')
        print(f'__connect_to_service {self.client.services()}')
        primary_service: list[QBluetoothUuid] = [
            s for s in self.client.services() if self.service_uuid.toString().upper() in s.toString().upper()
        ]
        if not primary_service:
            msg = f"Could not find primary service on {self.__sensor_address()}."
            logging.debug(msg)
            raise Exception(msg)
        logging.debug(f'Connecting to service {primary_service[0].toString()} on {self.__sensor_address()}')
        self.service = self.client.createServiceObject(primary_service[0])
        if not self.service:
            msg = f"Couldn't establish connection to HR service on {self.__sensor_address()}."
            logging.debug(msg)
            raise Exception(msg)
        logging.debug(f'Connected to service {self.service.serviceUuid().toString()} on {self.__sensor_address()}')
        self.service.stateChanged.connect(self.__start_notifications)
        self.service.characteristicChanged.connect(self._data_handler)
        print(f'Discovering service details {self.service.serviceUuid().toString()} on {self.__sensor_address()}')
        logging.debug(f'Discovering service details {self.service.serviceUuid().toString()} on {self.__sensor_address()}')
        self.service.discoverDetails()

    def __start_notifications(self, state: QLowEnergyService.ServiceState):
        self.status_update.emit('Subscribing to notifications...')
        if state != QLowEnergyService.ServiceState.RemoteServiceDiscovered:
            return
        if self.service is None:
            return
        for uuid in self.notification_uuids:
            msg = f"Subscribing to notifications for {uuid} on {self.__sensor_address()}."
            logging.debug(msg)
            print(msg)
            characteristic_uuid = QBluetoothUuid(QUuid(uuid))
            characteristic = self.service.characteristic(characteristic_uuid)
            if not characteristic.isValid():
                msg = f"Couldn't find characteristic {uuid} on {self.__sensor_address()}."
                logging.debug(msg)
                raise(msg)
            # Get the descriptor for client characteristic configuration
            descriptor = characteristic.descriptor(
                QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
            )
            if not descriptor.isValid():
                msg = f"Characteristic descriptor is invalid for {uuid} on {self.ble_device.remoteAddress().toString()}."
                logging.debug(msg)
                raise(msg)
            self.notifications.append(descriptor)
            # Subscribe to notifications for the characteristic
            self.service.writeDescriptor(descriptor, self.ENABLE_NOTIFICATION)
            print(f'Subscribed to notifications for {uuid} on {self.__sensor_address()}')

    def __reset_connection(self) -> None:
        self.disconnected.emit('Disconnected')
        logging.debug(f"Disconnected from device, cleaning up")
        self.__remove_service()
        self.__remove_client()
        self.ble_device = None

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
            self.notifications = []

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

    def _data_handler(self, _, data: QByteArray):  # _ is unused but mandatory argument
        """
        `data` GATT data
        """
        print(f'received data from {self.ble_device.name()} at {self.__sensor_address()}: {data.toStdString()}')
import logging
from typing import Callable, Optional

from PySide6.QtBluetooth import QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyService, QLowEnergyController, \
    QLowEnergyCharacteristic
from PySide6.QtCore import QObject, QByteArray, Signal, QTimer


class BluetoothDeviceService(QObject):

    ENABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0100")
    DISABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0000")

    error = Signal(tuple)
    notifications_subscribed = Signal(QBluetoothUuid)
    status_update = Signal(str, str)
    services_discovered = Signal(QBluetoothUuid)

    def __init__(self,
                 ble_device: QBluetoothDeviceInfo,
                 service_uuid: QBluetoothUuid,
                 characteristic_uuids: Optional[list[QBluetoothUuid]],
                 notification_handler: Optional[Callable],
                 read_handler: Optional[Callable]) -> None:
        super().__init__()
        self._service_uuid: QBluetoothUuid = service_uuid
        self._characteristic_uuids: list[QBluetoothUuid] = characteristic_uuids
        self._notification_handler: Optional[Callable] = notification_handler
        self._read_handler: Optional[Callable] = read_handler
        self._service: Optional[QLowEnergyService] = None
        self._notifications = []
        self._ble_device: QBluetoothDeviceInfo = ble_device

    def connect_to_service(self,
                           discovered_services: list[QBluetoothUuid],
                           controller: QLowEnergyController) -> None:
        service: list[QBluetoothUuid] = [
            s for s in discovered_services if self._service_uuid.toString().upper() in s.toString().upper()
        ]
        if not service:
            msg = f"Could not find service{self._service_uuid.toString()} on device {self._ble_device.name()}"
            logging.debug(msg)
            self.error.emit(msg)
            return
        logging.debug(f'Connecting to service {service[0].toString()}')
        self._service = controller.createServiceObject(service[0])
        if not self._service:
            msg = f"Couldn't establish connection to service {self._service_uuid.toString()} on device {self._ble_device.name()}."
            logging.debug(msg)
            self.error.emit(msg)
            return
        logging.debug(f'Connected to service {self._service.serviceUuid().toString()}')
        self._service.stateChanged.connect(self.__service_state_changed)
        self._service.characteristicChanged.connect(self._notification_handler)
        print(f'Discovering service details {self._service.serviceUuid().toString()}')
        logging.debug(f'Discovering service details {self._service.serviceUuid().toString()}')
        QTimer().singleShot(250, lambda: self._service.discoverDetails())

    def __service_state_changed(self, state: QLowEnergyService.ServiceState) -> None:
        print(f'__service_state_changed for service {self._service_uuid.toString()} state: {state} {QLowEnergyService.ServiceState.RemoteServiceDiscovered}')
        logging.debug(f'Service state changed: {state}')
        if state != QLowEnergyService.ServiceState.RemoteServiceDiscovered:
            return
        if self._service is None:
            return
        logging.debug(f'Characteristics for service {self._service_uuid.toString()} has been discovered: {state}')
        if self._notification_handler is not None and self._characteristic_uuids is not None:
            self.subscribe_to_notifications()
        if self._read_handler is not None:
            self._service.characteristicRead.connect(self._read_handler)
        self.services_discovered.emit(self._service_uuid)

    def subscribe_to_notifications(self) -> None:
        self.status_update.emit('Subscribing...', self._ble_device.name())
        for uuid in self._characteristic_uuids:
            msg = f"Subscribing to notifications for service: {self._service_uuid.toString()} characteristic: {uuid.toString()} on {self._ble_device.name()}."
            logging.debug(msg)
            print(msg)
            characteristic = self._service.characteristic(uuid)
            if not characteristic.isValid():
                msg = f"Couldn't find characteristic {uuid.toString()} on {self._ble_device.name()}."
                logging.debug(msg)
                self.error.emit(msg)
                return
            # Get the descriptor for client characteristic configuration
            descriptor = characteristic.descriptor(
                QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
            )
            if not descriptor.isValid():
                msg = f"Characteristic descriptor is invalid for {uuid.toString()} on {self._ble_device.name()}."
                logging.debug(msg)
                self.error.emit(msg)
                return
            self._notifications.append(descriptor)
            # Subscribe to notifications for the characteristic
            self._service.writeDescriptor(descriptor, BluetoothDeviceService.ENABLE_NOTIFICATION)
            print(f'Subscribed to notifications for {uuid.toString()} on {self._ble_device.name()}')
        self.notifications_subscribed.emit(self._service_uuid)

    def unsubscribe_from_notifications(self) -> None:
        if len(self._notifications) > 0 and self._service is not None:
            logging.debug('Unsubscribing from notifications')
            print('Unsubscribing from notifications')
            for notification in self._notifications:
                if notification.isValid():
                    self._service.writeDescriptor(notification, BluetoothDeviceService.DISABLE_NOTIFICATION)
            self._notifications.clear()

    def write_characteristic(self, characteristic_uuid: QBluetoothUuid, data: bytearray) -> None:
        if self._service is None:
            self.error.emit('Service not initialized')
            return
        characteristic = self._service.characteristic(characteristic_uuid)
        if characteristic.isValid() and QLowEnergyCharacteristic.PropertyType.Write & characteristic.properties():
            # Write the characteristic
            self._service.writeCharacteristic(characteristic, QByteArray(data))
        else:
            self.error.emit(f'Characteristic: {characteristic_uuid.toString()} not found or not writable')

    def read_characteristic(self, characteristic_uuid: QBluetoothUuid) -> None:
        if self._service is None:
            self.error.emit('Service not initialized')
            return
        characteristic = self._service.characteristic(characteristic_uuid)
        if characteristic.isValid() and QLowEnergyCharacteristic.PropertyType.Read & characteristic.properties():
            # Read the characteristic
            self._service.readCharacteristic(characteristic)
        else:
            self.error.emit(f'Characteristic: {characteristic_uuid.toString()} not found or not readable')

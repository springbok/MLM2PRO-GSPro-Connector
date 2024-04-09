import logging
from typing import List, Union

from PySide6.QtBluetooth import QLowEnergyCharacteristic, QBluetoothUuid
from PySide6.QtCore import QByteArray, QTimer
from simplepyble import Peripheral

from src.bluetooth.bluetooth_client_simpleble import BluetoothClientSimpleBLE
from src.bluetooth.bluetooth_device_base import BluetoothDeviceBase


class BluetoothDeviceBaseSimpleBLE(BluetoothDeviceBase):

    def __init__(self, device: Peripheral,
                 service_uuid: QBluetoothUuid, 
                 heartbeat_interval: int,
                 device_heartbeat_interval: int) -> None:
        super().__init__(service_uuid,
                 heartbeat_interval,
                 device_heartbeat_interval)
        self._ble_device = device
        self._service_uuid = self.__uuid_to_string(service_uuid)
        self._client: BluetoothClientSimpleBLE = BluetoothClientSimpleBLE(self._ble_device)
        self._client.connected.connect(self.__init_device)
        self._client.error.connect(self.__catch_error)
        self._client.disconnected.connect(self.__reset_connection)

    def connect_device(self):
        if self._ble_device is None:
            self.error.emit("No device to connect to.")
        else:
            self.status_update.emit('Connecting...', self._ble_device.identifier())
            msg = f'Connecting to {self._ble_device.identifier()} {self._ble_device.address()}'
            print(msg)
            logging.debug(msg)
            self._client.resume()

    def disconnect_device(self):
        if self._heartbeat_timer.isActive():
            self._heartbeat_timer.stop()
        if self._ble_device is not None and self._ble_device.is_connected():
            print('connected - disconnecting')
            if self._armed:
                self._disarm_device()
            print(f'self._notifications: {self._notifications}')
            logging.debug('Unsubscribing from notifications')
            print('Unsubscribing from notifications')
            for uuid in self._notifications:
                self._ble_device.unsubscribe(self._service_uuid, uuid)
                logging.info(f'Unsubscribed from notification {uuid}')
            self._notifications = []
            print('xxxx disconnecting')
            self.disconnecting.emit('Disconnecting...')
            self._ble_device.disconnect()

    def shutdown(self):
        print(f'{self.__class__.__name__} shutdown')
        if self._client is not None:
            self._client.shutdown()

    def __init_device(self):
        if self._subscribe_to_notifications():
            print('emit do_authenticate')
            QTimer().singleShot(1000, lambda: self.do_authenticate.emit())

    def _subscribe_to_notifications(self):
        services = self._ble_device.services()
        for service in services:
            print(f"    Service UUID: {service.uuid()}")
            print(f"    Service data: {service.data()}")
        self.status_update.emit('Subscribing...', self._ble_device.identifier())
        print(f'len(services): {len(services)} self._service_uuid: {self._service_uuid}')
        if len(services) <= 0 or not any(self._service_uuid == service.uuid() for service in services):
            msg = f"Could not find primary service {self._service_uuid} on {self._ble_device.address()}."
            logging.debug(msg)
            print(msg)
            self.error.emit(msg)
        else:
            try:
                self._notifications = []
                for uuid in self._notification_uuids:
                    msg = f"Subscribing to notifications for {uuid.toString()} on {self._ble_device.identifier()}"
                    logging.debug(msg)
                    print(msg)
                    print(f'self._service_uuid: {self._service_uuid} self.__uuid_to_string(uuid) {self.__uuid_to_string(uuid)}')
                    uuid_str = self.__uuid_to_string(uuid)
                    self._ble_device.notify(self._service_uuid,
                                            uuid_str,
                                            lambda data: print(f"Notification: {data}"))
                    print(f'Subscribed to notifications for {uuid_str} on {self._ble_device.identifier()}')
                    self._notifications.append(uuid_str)
            except Exception as e:
                self.error.emit(format(e))
                return False
            return True

    def _is_connected(self) -> bool:
        return self._ble_device is not None and self._ble_device.is_connected()

    def __reset_connection(self) -> None:
        self._client.disconnected.disconnect()
        print(f'{self.__class__.__name__} __reset_connection')
        logging.debug(f"Disconnected from device, cleaning up")
        self.disconnect_device()
        self._client.shutdown()
        self._ble_device = None
        self.disconnected.emit('Disconnected')

    def __catch_error(self, error) -> None:
        msg = f'An error has occurred: {error}'
        logging.debug(msg)
        self.error.emit(msg)
        self.__reset_connection()

    def __handle_data(data: bytes, uuid: QBluetoothUuid):
        print(f'Received {len(data)} bytes from {uuid.toString()}')


    def _data_handler(self, char: QLowEnergyCharacteristic, data: QByteArray):
        pass

    def __uuid_to_string(self, uuid: QBluetoothUuid):
        uuid_str = uuid.toString().lower().replace('{', '').replace('}', '')
        print(f'uuid_str: {uuid_str}')
        return uuid_str


    def _write_characteristic(self, characteristic_uuid: QBluetoothUuid, data: bytearray) -> None:
        if self._service is None:
            self.error.emit('Service not initialized')
            return
        characteristic = self._service.characteristic(characteristic_uuid)
        if characteristic.isValid() and QLowEnergyCharacteristic.PropertyType.Write & characteristic.properties():
            # Write the characteristic
            self._service.writeCharacteristic(characteristic, QByteArray(data))
        else:
            self.error.emit(f'Characteristic: {characteristic_uuid.toString()} not found or not writable')

import logging

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
        if self._ble_device is not None:
            logging.debug(f'Disconnecting from device: {self._ble_device.identifier()}')
        if self._heartbeat_timer.isActive():
            self._heartbeat_timer.stop()
        if self._ble_device.is_connected():
            print('connected - disconnecting')
            if self._armed:
                self._disarm_device()
            print(f'self._notification_uuids: {self._notification_uuids}')
            logging.debug('Unsubscribing from notifications')
            print('Unsubscribing from notifications')
            for uuid in self._notification_uuids:
                    self._ble_device.unsubscribe(uuid.toString())
                    logging.info(f'Unsubscribed from notification {uuid.toString()}')
            print('xxxx disconnecting')
            self.disconnecting.emit('Disconnecting...')
            self._ble_device.disconnect()

    def shutdown(self):
        self._client.shutdown()

    def __init_device(self):
        self._subscribe_to_notifications()
        print('emit do_authenticate')
        QTimer().singleShot(1000, lambda: self.do_authenticate.emit())

    def _subscribe_to_notifications(self):
        services = self._ble_device.services()
        for service in services:
            print(f"    Service UUID: {service.uuid()}")
            print(f"    Service data: {service.data()}")
        self.status_update.emit('Subscribing...', self._ble_device.identifier())
        try:
            for uuid in self._notification_uuids:
                msg = f"Subscribing to notifications for {uuid.toString()} on {self._ble_device.identifier()}"
                logging.debug(msg)
                print(msg)
                print(f'self._service_uuid: {self._service_uuid} self.__uuid_to_string(uuid) {self.__uuid_to_string(uuid)}')
                self._ble_device.notify(self._service_uuid,
                                        self.__uuid_to_string(uuid),
                                        lambda data: print(f"Notification: {data}"))
                print(f'Subscribed to notifications for {uuid.toString()} on {self._ble_device.identifier()}')
        except Exception as e:
            self.__catch_error(format(e))

    def _is_connected(self) -> bool:
        return self._ble_device is not None and self._ble_device.is_connected()

    def __reset_connection(self) -> None:
        self.disconnected.emit('Disconnected')
        logging.debug(f"Disconnected from device, cleaning up")
        #self._ble_device = None

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

import datetime
import logging

from PySide6.QtBluetooth import QLowEnergyController, QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyService
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from typing import Union

from src.appdata import AppDataPaths
from src.ball_data import BallData
from src.bluetooth.bluetooth_device_service import BluetoothDeviceService
from src.settings import Settings


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
    update_battery = Signal(int)
    shot = Signal(BallData)
    launch_monitor_connected = Signal()
    launch_monitor_event = Signal(str)

    def __init__(self, device: QBluetoothDeviceInfo,
                 services: list[BluetoothDeviceService],
                 heartbeat_interval: int,
                 device_heartbeat_interval: int) -> None:
        super().__init__()
        self._ble_device = device
        self._controller: Union[None, QLowEnergyController] = None
        self._services: list[BluetoothDeviceService] = services
        self._heartbeat_timer: QTimer = QTimer()
        self.heartbeat_interval = heartbeat_interval
        self._device_heartbeat_interval = device_heartbeat_interval
        self._set_next_expected_heartbeat()
        self._app_paths: AppDataPaths = AppDataPaths('mlm2pro-gspro-connect')
        self._settings: Settings = Settings(self._app_paths)
        self._armed: bool = False
        self._current_club: str = ''
        self._thread: QThread = QThread()
        self.moveToThread(self._thread)
        self._thread.start()

    def shutdown(self) -> None:
        print(f'{self.__class__.__name__} shutdown')
        self._thread.quit()
        self._thread.wait()
        #self._thread.deleteLater()

    def _sensor_address(self) -> str:
        return self._controller.remoteAddress().toString()

    def connect_device(self) -> None:
        if self._ble_device is None:
            self.error.emit("No device to connect to.")
            return
        print(f'connect_client {self._ble_device.name()}')
        if self._controller is not None:
            logging.debug(f"Currently connected to {self._ble_device.name()} at {self._sensor_address()}.")
            self.connected.emit('Connected')
            return
        print(f'Connecting to {self._ble_device.name()}')
        self.status_update.emit('Connecting...', self._ble_device.name())
        self._controller = QLowEnergyController.createCentral(self._ble_device)
        #self._controller.setRemoteAddressType(QLowEnergyController.RemoteAddressType.PublicAddress)
        self._controller.errorOccurred.connect(self.__catch_error)
        self._controller.connected.connect(self.__discover_services)
        self._controller.rssiRead.connect(self.__rssi_read)
        self._controller.serviceDiscovered.connect(self.__service_found)
        self._controller.discoveryFinished.connect(self.__connect_to_services)
        self._controller.disconnected.connect(self.__reset_connection)
        self.launch_monitor_connected.connect(self._connected)
        #self._controller.rssiRead.connect(self.__rssi_read)
        self._controller.disconnectFromDevice()
        self._controller.connectToDevice()
        self._heartbeat_timer.stop()
        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.setInterval(self.heartbeat_interval)
        self._heartbeat_timer.timeout.connect(self._heartbeat)
        self._heartbeat_timer.start()

    def _connected(self) -> None:
        self.connected.emit('Connected')
        self._set_next_expected_heartbeat()
        self._arm_device()
        self._armed = True

    def _arm_device(self) -> None:
        pass

    def _disarm_device(self) -> None:
        pass

    def club_selected(self, club: str) -> None:
        self._current_club = club

    def __rssi_read(self, rssi: int) -> None:
        self.rssi_read.emit(rssi)

    def __service_found(self, service_uuid: QBluetoothUuid) -> None:
        logging.debug(f'Found service: {service_uuid.toString()}')
        print(f'Found service: {service_uuid.toString()}')
        
    def _heartbeat(self) -> None:
        pass

    def disconnect_device(self) -> None:
        if self._ble_device is not None:
            logging.debug(f'Disconnecting from device: {self._ble_device.name()}')
        if self._controller is not None:
            print(f'disconnect_device {self._controller.state()}')
            self._controller.errorOccurred.disconnect()
            self._controller.disconnected.disconnect()
            if self._heartbeat_timer.isActive():
                self._heartbeat_timer.stop()
            if self._controller.state() == QLowEnergyController.ControllerState.DiscoveredState:
                print('connected - disconnecting')
                if self._armed:
                    self._disarm_device()
                for service in self._services:
                    service.unsubscribe_from_notifications()
            if self._controller.state() == QLowEnergyController.ControllerState.DiscoveredState or \
                    self._controller.state() == QLowEnergyController.ControllerState.ConnectedState:
                print('xxxx disconnecting')
                self.disconnecting.emit('Disconnecting...')
                self._controller.disconnectFromDevice()
        self.__remove_services()
        self.__remove_client()
        self._ble_device = None

    def __discover_services(self) -> None:
        print(f'discover services state: {self._controller.state()}')
        if self._controller is not None:
            logging.debug(f'Discovering services for {self._ble_device.name()}')
            self.status_update.emit('Discovering services...', self._ble_device.name())
            QTimer().singleShot(250, lambda: self._controller.discoverServices())

    def __connect_to_services(self) -> None:
        logging.debug(f'Discovered services: {self._controller.services()}')
        self.status_update.emit('Connecting to services...', self._ble_device.name())
        print(f'__connect_to_service {self._controller.services()}')
        for service in self._services:
            self._connect_to_service(service)

    def _connect_to_service(self, service: BluetoothDeviceService) -> None:
        service.connect_to_service(self._controller.services(), self._controller)
        service.status_update.connect(self.status_update.emit)
        service.error.connect(self.__catch_error)

    def _is_connected(self) -> bool:
        return self._controller and self._controller.state() == QLowEnergyController.ControllerState.DiscoveredState

    def __reset_connection(self) -> None:
        self.disconnected.emit('Disconnected')
        logging.debug(f"Disconnected from device, cleaning up")
        self.error.emit('Unexpected disconnection')

    def __remove_services(self) -> None:
        if self._services is None:
            return
        try:
            print('Deleting bluetooth services')
            logging.debug('Deleting bluetooth services')
            for service in self._services:
                service.deleteLater()
        except Exception as e:
            logging.debug(f"Couldn't remove service: {e}")
        finally:
            self._services = None

    def __remove_client(self) -> None:
        if self._controller is None:
            return
        try:
            print('Deleting bluetooth client')
            logging.debug('Deleting bluetooth client')
            #self._controller.disconnected.disconnect()
            self._controller.deleteLater()
        except Exception as e:
            print(f"Couldn't remove client: {e}")
        finally:
            self._controller = None

    def __catch_error(self, error) -> None:
        if error == QLowEnergyController.Error.ConnectionError:
            msg = f'Make sure the device is turned on and in range, error: {error}'
        elif error == QLowEnergyController.Error.AuthorizationError:
            msg = f'The device is not authorized to connect to the device, error: {error}'
        else:
            msg = f'An error has occurred: {error}'
        if self._controller is not None:
            msg = f'{self._controller.errorString()} {msg}'
        logging.debug(msg)
        self.error.emit(msg)

    def _set_next_expected_heartbeat(self) -> None:
        now = datetime.datetime.utcnow()
        self._next_heartbeat = now + datetime.timedelta(seconds=self._device_heartbeat_interval)
        #logging.debug(f'Next heartbeat expected at {self._next_heartbeat} now: {now}')

    @property
    def _heartbeat_overdue(self) -> bool:
        return datetime.datetime.utcnow() > self._next_heartbeat

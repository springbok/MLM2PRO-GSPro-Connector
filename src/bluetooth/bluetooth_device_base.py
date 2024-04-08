import datetime
from typing import List

from PySide6.QtBluetooth import QBluetoothUuid
from PySide6.QtCore import QObject, QByteArray, Signal, QTimer

from src.appdata import AppDataPaths
from src.ball_data import BallData
from src.settings import Settings


class BluetoothDeviceBase(QObject):

    error = Signal(str)
    disconnecting = Signal(str)
    disconnected = Signal(str)
    connecting = Signal(str)
    connected = Signal(str)
    status_update = Signal(str, str)
    rssi_read = Signal(int)
    do_authenticate = Signal()
    update_battery = Signal(int)
    shot = Signal(BallData)
    launch_monitor_connected = Signal()

    def __init__(self,
                 service_uuid: QBluetoothUuid,
                 heartbeat_interval: int,
                 device_heartbeat_interval: int) -> None:
        super().__init__()
        self._service_uuid: QBluetoothUuid = service_uuid
        self._notification_uuids: List[QBluetoothUuid] = []
        self._notifications = []
        self.ENABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0100")
        self.DISABLE_NOTIFICATION: QByteArray = QByteArray.fromHex(b"0000")
        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.setInterval(heartbeat_interval)
        self._heartbeat_timer.timeout.connect(self._heartbeat)
        self._device_heartbeat_interval = device_heartbeat_interval
        self._set_next_expected_heartbeat()
        self._app_paths = AppDataPaths('mlm2pro-gspro-connect')
        self._settings = Settings(self._app_paths)
        self._armed: bool = False
        self._current_club: str = ''

    def _sensor_address(self) -> str:
        pass

    def connect_device(self) -> None:
        pass

    def _connected(self):
        print('connected')
        self.connected.emit('Connected')
        self._set_next_expected_heartbeat()
        self._heartbeat_timer.start()
        self._arm_device()
        self._armed = True

    def _arm_device(self) -> None:
        pass

    def _disarm_device(self) -> None:
        pass

    def club_selected(self, club: str):
        self._current_club = club

    def _rssi_read(self, rssi: int) -> None:
        self.rssi_read.emit(rssi)

    def _heartbeat(self) -> None:
        pass

    def disconnect_device(self) -> None:
        pass

    def _authenticate(self) -> None:
        pass

    def _is_connected(self) -> bool:
        pass

    def _write_characteristic(self, characteristic_uuid: str, data: bytearray) -> None:
        pass

    def _set_next_expected_heartbeat(self) -> None:
        now = datetime.datetime.utcnow()
        self._next_heartbeat = now + datetime.timedelta(seconds=self._device_heartbeat_interval)
        #logging.debug(f'Next heartbeat expected at {self._next_heartbeat} now: {now}')

    @property
    def _heartbeat_overdue(self) -> None:
        return datetime.datetime.utcnow() > self._next_heartbeat

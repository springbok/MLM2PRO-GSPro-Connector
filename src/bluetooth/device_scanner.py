import logging
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent
from PySide6.QtCore import QObject, Signal


class DeviceScanner(QObject):
    device_update = Signal(object)
    status_update = Signal(str)
    scan_error = Signal(str)

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self.launch_minitor_names = launch_minitor_names
        self.scanner = QBluetoothDeviceDiscoveryAgent()
        self.scanner.finished.connect(self._handle_scan_result)
        self.scanner.errorOccurred.connect(self._handle_scan_error)

    def scan(self):
        if self.scanner.isActive():
            logging.debug("Already searching for sensors.")
            return
        logging.debug(f'Searching for following launch monitor names: {self.launch_minitor_names}')
        self.status_update.emit("Scanning...")
        self.scanner.start(QBluetoothDeviceDiscoveryAgent.supportedDiscoveryMethods().LowEnergyMethod)

    def _handle_scan_result(self):
        self.device = None
        for d in self.scanner.discoveredDevices():
            logging.debug(f'Found device: {d.name()} uuid: {d.deviceUuid().toString()}')
            if d.name() and any(d.name().startswith(name) for name in self.launch_minitor_names):
                self.device = d
                break
        if self.device is not None:
            logging.debug(f'Launch monitor found: {self.device.name()} uuid: {self.device.deviceUuid().toString()}')
            self.status_update.emit('Device found')
            self.device_update.emit(self.device)

    def _handle_scan_error(self, error):
        logging.debug(f'Error while scanning for device {error}')
        self.scan_error.emit(error)

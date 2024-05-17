import logging
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
from PySide6.QtCore import QObject, Signal, QTimer


class BluetoothDeviceScanner(QObject):
    SCANNER_TIMEOUT = 40000

    device_found = Signal(object)
    device_not_found = Signal()
    status_update = Signal(str)
    error = Signal(str)

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self.launch_minitor_names = launch_minitor_names
        self.scanner = QBluetoothDeviceDiscoveryAgent()
        #self.scanner.setLowEnergyDiscoveryTimeout(BluetoothDeviceScanner.SCANNER_TIMEOUT*1000)
        self.scanner.deviceDiscovered.connect(self.__add_device)
        self.scanner.errorOccurred.connect(self.__handle_scan_error)
        self.scanner.finished.connect(self.__scanning_finished)
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.setInterval(BluetoothDeviceScanner.SCANNER_TIMEOUT)
        self.scan_timer.timeout.connect(self.stop_scanning)
        self.device = None

    def scan(self) -> None:
        print(f'scan timeout {self.scanner.lowEnergyDiscoveryTimeout()}')
        if self.scanner.isActive():
            logging.debug("Already searching for device.")
        else:
            logging.debug(f'Searching for the following launch monitor names: {self.launch_minitor_names}')
            self.status_update.emit("Scanning for device...")
            self.scanner.start(QBluetoothDeviceDiscoveryAgent.supportedDiscoveryMethods().LowEnergyMethod)
            # For some reason the setLowEnergyDiscoveryTimeout doesn't work
            self.scan_timer.start()

    def stop_scanning(self) -> None:
        self.scan_timer.stop()
        if self.scanner.isActive():
            self.scanner.stop()
        if self.device is None:
            logging.debug('Timeout, no device found')
            self.status_update.emit('Timeout')
            self.device_not_found.emit()

    def __add_device(self, device) -> None:
        print(f'info: {device.name()} self.launch_minitor_names: {self.launch_minitor_names}')
        print(f'found: {device.name() and any(device.name().startswith(name) for name in self.launch_minitor_names)}')
        if device.coreConfigurations() & QBluetoothDeviceInfo.CoreConfiguration.LowEnergyCoreConfiguration and \
                device.name() and any(device.name().startswith(name) for name in self.launch_minitor_names):
            self.device = device
            self.scanner.stop()
            self.scan_timer.stop()
            logging.debug(f'Launch monitor found: {self.device.name()} uuid: {self.device.address().toString()}')
            print(f'Launch monitor found: {self.device.name()} uuid: {self.device.address().toString()}')
            self.status_update.emit('Device found')
            self.device_found.emit(self.device)

    def __handle_scan_error(self, error) -> None:
        logging.debug(f'Error while scanning for device {error}')
        self.error.emit(error)

    def __scanning_finished(self) -> None:
        self.scan_timer.stop()
        if self.device is None:
            logging.debug('No device found')
            self.status_update.emit('No device found')
            self.device_not_found.emit()

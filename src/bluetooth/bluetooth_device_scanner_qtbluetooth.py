import logging
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
from PySide6.QtCore import QObject, QTimer

from src.bluetooth.bluetooth_device_scanner_signals import BluetoothDeviceScannerSignals


class BluetoothDeviceScannerQtBluetooth(QObject):
    SCANNER_TIMEOUT = 40000

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self.signals = BluetoothDeviceScannerSignals()
        self._launch_minitor_names = launch_minitor_names
        self._scanner = QBluetoothDeviceDiscoveryAgent()
        #self._scanner.setLowEnergyDiscoveryTimeout(BluetoothDeviceScanner.SCANNER_TIMEOUT*1000)
        self._scanner.deviceDiscovered.connect(self.__add_device)
        self._scanner.errorOccurred.connect(self.__handle_scan_error)
        self._scanner.finished.connect(self.__scanning_finished)
        self.scan_timer: QTimer = QTimer()
        self._device: QBluetoothDeviceInfo = None

    def scan(self) -> None:
        print(f'scan timeout {self._scanner.lowEnergyDiscoveryTimeout()}')
        if self._scanner.isActive():
            logging.debug("Already searching for device.")
        else:
            logging.debug(f'Searching for the following launch monitor names: {self._launch_minitor_names}')
            self.signals.status_update.emit("Scanning for device...")
            self._scanner.start(QBluetoothDeviceDiscoveryAgent.supportedDiscoveryMethods().LowEnergyMethod)
            # For some reason the setLowEnergyDiscoveryTimeout doesn't work
            self.scan_timer.setSingleShot(True)
            self.scan_timer.setInterval(BluetoothDeviceScannerQtBluetooth.SCANNER_TIMEOUT)
            self.scan_timer.timeout.connect(self.stop_scanning)
            self.scan_timer.start()

    def stop_scanning(self) -> None:
        if self._scanner.isActive():
            self._scanner.stop()
        if self._device is None:
            logging.debug('Timeout, no device found')
            self.signals.status_update.emit('Timeout')
            self.signals.device_not_found.emit()

    def __add_device(self, device) -> None:
        print(f'info: {device.name()} {device.name().startswith("MLM2-") or device.name().startswith("BlueZ ")}')
        if device.coreConfigurations() & QBluetoothDeviceInfo.CoreConfiguration.LowEnergyCoreConfiguration and \
                device.name() and any(device.name().startswith(name) for name in self._launch_minitor_names):
            self._device = device
            self._scanner.stop()
            logging.debug(f'Launch monitor found: {self._device.name()} uuid: {self._device.address().toString()}')
            print(f'Launch monitor found: {self._device.name()} uuid: {self._device.address().toString()}')
            self.signals.status_update.emit('Device found')
            self.signals.device_found.emit(self._device)

    def __handle_scan_error(self, error) -> None:
        logging.debug(f'Error while scanning for device {error}')
        self.signals.error.emit(error)

    def __scanning_finished(self) -> None:
        if self._device is None:
            logging.debug('No device found')
            self.signals.status_update.emit('No device found')
            self.signals.device_not_found.emit()
        self._scan_timer.stop()

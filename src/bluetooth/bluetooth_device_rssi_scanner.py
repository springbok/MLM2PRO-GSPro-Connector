import logging
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo
from PySide6.QtCore import QObject, Signal, QTimer


class BluetoothDeviceRssiScanner(QObject):
    SCANNER_TIMEOUT = 3000

    rssi = Signal(int)
    finished = Signal()

    def __init__(self, launch_minitor_names: list[str]):
        super().__init__()
        self.launch_minitor_names = launch_minitor_names
        self.scanner = QBluetoothDeviceDiscoveryAgent()
        self.scanner.deviceDiscovered.connect(self.__add_device)
        self.scanner.finished.connect(self.__scanning_finished)
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.setInterval(BluetoothDeviceRssiScanner.SCANNER_TIMEOUT)
        self.scan_timer.timeout.connect(self.stop_scanning)
        self.previous_rssi = 1

    def scan(self) -> None:
        if self.scanner.isActive():
            logging.debug("Already searching for device.")
        else:
            self.scanner.start(QBluetoothDeviceDiscoveryAgent.supportedDiscoveryMethods().LowEnergyMethod)
            # For some reason the setLowEnergyDiscoveryTimeout doesn't work
            self.scan_timer.start()

    def stop_scanning(self) -> None:
        self.scan_timer.stop()
        if self.scanner.isActive():
            self.scanner.stop()

    def __add_device(self, device) -> None:
        if device.coreConfigurations() & QBluetoothDeviceInfo.CoreConfiguration.LowEnergyCoreConfiguration and \
                device.name() and any(device.name().startswith(name) for name in self.launch_minitor_names):
            if device.rssi() < 0 and device.rssi() != self.previous_rssi:
                #logging.debug(f"RSSI updated for {device.name()} RSSI: {device.rssi()}")
                self.previous_rssi = device.rssi()
                self.rssi.emit(device.rssi())
            self.stop_scanning()

    def __scanning_finished(self) -> None:
        self.scan_timer.stop()
        self.finished.emit()

from PySide6.QtCore import QObject, Signal


class BluetoothDeviceScannerSignals(QObject):

    device_found = Signal(object)
    device_not_found = Signal()
    status_update = Signal(str)
    error = Signal(str)

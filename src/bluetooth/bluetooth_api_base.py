from PySide6.QtCore import QObject

class BluetoothAPIBase(QObject):

    def __init__(self):
        self.connected = False
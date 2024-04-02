import sys
from PySide6.QtCore import Qt, QIODeviceBase, QUuid
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget, QWidget
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothServiceDiscoveryAgent, QBluetoothSocket, \
    QBluetoothUuid, QBluetoothServiceInfo, QBluetoothAddress


class BluetoothApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bluetooth App")

        self.device_list_widget = QListWidget()
        self.device_list_widget.itemDoubleClicked.connect(self.connect_to_device)
        self.info = None

        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.scan_devices)

        layout = QVBoxLayout()
        layout.addWidget(self.device_list_widget)
        layout.addWidget(self.scan_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.bluetooth_agent = QBluetoothDeviceDiscoveryAgent()
        self.bluetooth_agent.deviceDiscovered.connect(self.add_device_to_list)

    def scan_devices(self):
        self.device_list_widget.clear()
        self.bluetooth_agent.start()

    def add_device_to_list(self, info):
        self.device_list_widget.addItem(info.name())
        if info.name().startswith("MLM2"):
            self.info = info

    def connect_to_device(self, item):
        selected_device = item.text()
        self.bluetooth_agent.stop()
        socket = QBluetoothSocket(QBluetoothServiceInfo.Protocol.RfcommProtocol)
        service_uuid = QBluetoothUuid(QUuid('{DAF9B2A4-E4DB-4BE4-816D-298A050F25CD}'))
        # socket.readyRead.connect(self._read_socket)
        socket.errorOccurred.connect(self.__catch_error)
        socket.connected.connect(self.__connected)
        print(f'bef conn {self.info.address().toString()} {service_uuid.toString()}')
        socket.connectToService(self.info.address(), service_uuid,
                                QIODeviceBase.OpenModeFlag.ReadWrite)
        print('aft conn')
        '''
        if socket.state() == QBluetoothSocket.SocketState.ConnectedState:
            # socket.connectToService(self.info.address())
            print(f"Connected to {selected_device}")
        else:
            print(f"Failed to connect to {selected_device}")

        self.discover_services(self.info.address())
        '''

    def __connected(self):
        print("Connected")

    def discover_services(self, address):
        print(f'discover_services address: {address}')
        print('discover_services')
        service_agent = QBluetoothServiceDiscoveryAgent(address)
        service_agent.serviceDiscovered.connect(self.service_discovered)
        service_agent.errorOccurred.connect(self.__catch_error)
        service_agent.finished.connect(self.service_discovery_finished)
        service_agent.start()

    def __catch_error(self, error):
        print("Error:", error)

    def service_discovered(self, info):
        print("Service discovered:")
        print("  Service Name:", info.serviceName())
        print("  Service UUID:", info.serviceUuid().toString())

    def service_discovery_finished(self):
        print("Service discovery finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BluetoothApp()
    window.show()
    sys.exit(app.exec())

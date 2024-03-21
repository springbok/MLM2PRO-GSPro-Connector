from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtBluetooth import (QBluetoothAddress, QBluetoothServiceInfo,
                                 QBluetoothServiceDiscoveryAgent, QBluetoothLocalDevice)

from service_ui import Ui_ServiceDiscovery


class ServiceDiscoveryDialog(QDialog):
    def __init__(self, name, address, parent=None):
        print('init')
        super().__init__(parent)
        self._ui = Ui_ServiceDiscovery()
        self._ui.setupUi(self)

        # Using default Bluetooth adapter
        local_device = QBluetoothLocalDevice()
        adapter_address = QBluetoothAddress(local_device.address())
        print(f'adapter_address: {adapter_address.toString()}')

        # In case of multiple Bluetooth adapters it is possible to
        # set which adapter will be used by providing MAC Address.
        # Example code:
        #
        # adapterAddress = QBluetoothAddress("XX:XX:XX:XX:XX:XX")
        # discoveryAgent = QBluetoothServiceDiscoveryAgent(adapterAddress)

        self._discovery_agent = QBluetoothServiceDiscoveryAgent(adapter_address)
        self._discovery_agent.setRemoteAddress(address)

        self.setWindowTitle(name)

        self._discovery_agent.serviceDiscovered.connect(self.add_service)
        self._discovery_agent.finished.connect(self._ui.status.hide)
        self._discovery_agent.start()

    @Slot(QBluetoothServiceInfo)
    def add_service(self, info):
        print('add service')
        line = info.serviceName()
        if not line:
            return

        if info.serviceDescription():
            line += "\n\t" + info.serviceDescription()
        if info.serviceProvider():
            line += "\n\t" + info.serviceProvider()
        self._ui.list.addItem(line)
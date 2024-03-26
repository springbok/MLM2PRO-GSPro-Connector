from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtBluetooth import QLowEnergyService


class ServiceInfo(QObject):

    service_changed = Signal()

    def __init__(self, service: QLowEnergyService) -> None:
        super().__init__()
        self.service = service
        self.service.setParent(self)

    @Property(str, notify=service_changed)
    def service_name(self):
        if not self.service:
            return ""

        return self.service.service_name()

    @Property(str, notify=service_changed)
    def service_type(self):
        if not self.service:
            return ""

        result = ""
        if (self.service.type() & QLowEnergyService.PrimaryService):
            result += "primary"
        else:
            result += "secondary"

        if (self.service.type() & QLowEnergyService.IncludedService):
            result += " included"

        result = '<' + result + '>'

        return result

    @Property(str, notify=service_changed)
    def service_uuid(self):
        if not self.service:
            return ""

        uuid = self.service.serviceUuid()
        result16, success16 = uuid.toUInt16()
        if success16:
            return f"0x{result16:x}"

        result32, sucesss32 = uuid.toUInt32()
        if sucesss32:
            return f"0x{result32:x}"

        return uuid.toString().replace('{', '').replace('}', '')

from dataclasses import dataclass
from enum import Flag, auto


@dataclass
class LogMessageSystems:
    CONNECTOR = 'Connector'
    GSPRO_CONNECT = 'GSProConnect'
    WEBCAM_PUTTING = "Webcam Putting"
    EXPUTT_PUTTING = "ExPutt"


@dataclass
class LogMessageTypes(Flag):
    STATUS_BAR = auto()
    LOG_WINDOW = auto()
    LOG_FILE = auto()
    ALL = STATUS_BAR | LOG_WINDOW | LOG_FILE
    LOGS = LOG_WINDOW | LOG_FILE
    UI = STATUS_BAR | LOG_WINDOW


@dataclass
class LogMessage:
    message_types: LogMessageTypes
    message_system: str
    message: str

    def message_string(self):
        return f'{self.message_system}: {self.message}'

    def display_on(self, message_type=None):
        return message_type in self.message_types

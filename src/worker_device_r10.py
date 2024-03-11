import logging
import socket
import traceback
from threading import Event

from PySide6.QtCore import QObject, Signal

from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceR10(WorkerBase):

    shot = Signal(object or None)
    listening = Signal()
    connected = Signal()
    finished = Signal()

    def __init__(self, settings: Settings):
        WorkerBase.__init__(self)
        self.settings = settings
        self.name = 'WorkerDeviceR10'
        self.connection = None
        self._shutdown = Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)

    def run(self) -> None:
        try:
            print('started')
            self.started.emit()
            self._pause.wait()
            self._socket.bind((self.settings.r10_connector_ip_address, self.settings.r10_connector_port))
            self._socket.listen(1)
            msg = f"Listening for R10 on port {self.settings.r10_connector_ip_address} : {self.settings.r10_connector_port}"
            self.listening.emit()
            logging.debug(f'{self.name}: {msg}')
            while not self._shutdown.is_set():
                try:
                    # Wait for connection
                    self.connection, addr = self._socket.accept()
                    self.connection.settimeout(1)
                except socket.timeout:
                    pass
                else:
                    msg = f"Connected to R10 from: {addr[0]}:{addr[1]}"
                    self.connected.emit()
                    logging.debug(f'{self.name}: {msg}')
                    while not self._shutdown.is_set():
                        try:
                            # Wait for data
                            data = self.connection.recv(1024)
                            if data is not None and len(data) > 0:
                                logging.debug(f'{self.name}: R10 received data: {data.decode()}')
                                self.shot.emit(data)
                            else:
                                break
                        except socket.timeout:
                            pass
                        except ConnectionError:
                            logging.debug(f'{self.name}: R10 disconnected')
                            break
                        finally:
                            self.connection.close()
                            break
        except Exception as e:
            logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
        finally:
            print('finished')
            if self._socket:
                self._socket.close()
        self.finished.emit()

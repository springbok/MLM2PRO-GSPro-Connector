import json
import logging
import socket
import traceback
from threading import Event

from PySide6.QtCore import Signal

from src.gspro_connect import GSProConnect
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceR10(WorkerBase):

    r10_shot = Signal(object or None)
    listening = Signal()
    connected = Signal()
    finished = Signal()

    def __init__(self, settings: Settings, gspro_connection: GSProConnect):
        WorkerBase.__init__(self)
        self.settings = settings
        self.gspro_connection = gspro_connection
        self.name = 'WorkerDeviceR10'
        self.connection = None
        self._shutdown = Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)

    def run(self) -> None:
        try:
            self.started.emit()
            self._pause.wait()
            self._socket.bind((self.settings.r10_connector_ip_address, self.settings.r10_connector_port))
            self._socket.listen(5)
            msg = f"Listening for R10 on port {self.settings.r10_connector_ip_address} : {self.settings.r10_connector_port}"
            self.listening.emit()
            logging.debug(f'{self.name}: {msg}')
            while not self._shutdown.is_set():
                try:
                    # Wait for connection
                    self.connection, addr = self._socket.accept()
                    #self.connection.settimeout(1)
                except socket.timeout:
                    pass
                else:
                    msg = f"Connected to R10 from: {addr[0]}:{addr[1]}"
                    self.connected.emit()
                    logging.debug(f'{self.name}: {msg}')
                    while not self._shutdown.is_set():
                        self._pause.wait()
                        try:
                            # Wait for data
                            print(f'{self.name}: R10 waiting for data')
                            data = self.connection.recv(1024)
                            if data is not None and len(data) > 0:
                                print(f'{self.name}: R10 received data: {data.decode()}')
                                logging.debug(f'{self.name}: R10 received data: {data.decode()}')
                                if self.gspro_connection.connected():
                                    msg = self.gspro_connection.send_msg(data)
                                    self.send_msg(msg)
                                    self.r10_shot.emit(data)
                                    logging.debug(f'{self.name}: R10 sent data to GSPro result: {msg.decode()}')
                            else:
                                break
                        except socket.timeout:
                            pass
                        except ConnectionError:
                            logging.debug(f'{self.name}: R10 disconnected')
                            break
                        except Exception as e:
                            raise e
        except Exception as e:
            logging.debug(f'Error in process {self.name}: {format(e)}, {traceback.format_exc()}')
            self.error.emit((e, traceback.format_exc()))
        finally:
            if self._socket:
                self._socket.close()
        self.finished.emit()

    def club_selected(self, club):
        super().club_selected(club)
        if self.putter_selected():
            logging.debug('Putter selected pausing shot processing')
            self.pause()
        else:
            self.resume()
            logging.debug('Club other than putter selected resuming shot processing')

    def send_msg(self, payload, attempts=2):
        if self.connection:
            for attempt in range(attempts):
                try:
                    print(f'send_msg: {payload}')
                    self.connection.sendall(payload)
                except Exception as e:
                    msg = f"R10 unknown error when trying to send result, Exception: {format(e)}"
                    logging.debug(msg)
                    raise Exception(msg)

    def shutdown(self):
        super().shutdown()
        if self.connection:
            self.connection.close()

import logging
import socket
import traceback
from threading import Event

from PySide6.QtCore import Signal

from src.gspro_connect import GSProConnect
from src.settings import Settings
from src.worker_base import WorkerBase


class WorkerDeviceLaunchMonitorRelayServer(WorkerBase):

    relay_server_shot = Signal(object or None)
    listening = Signal()
    connected = Signal()
    finished = Signal()
    shot_error = Signal(tuple)
    disconnected = Signal()

    def __init__(self, settings: Settings, gspro_connection: GSProConnect):
        WorkerBase.__init__(self)
        self.settings = settings
        self.gspro_connection = gspro_connection
        self.name = 'WorkerDeviceLaunchMonitorRelayServer'
        self.connection = None
        self._shutdown = Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)

    def run(self) -> None:
        try:
            self.started.emit()
            self._pause.wait()
            self._socket.bind((self.settings.relay_server_ip_address, self.settings.relay_server_port))
            self._socket.listen(5)
            msg = f"Listening on port {self.settings.relay_server_ip_address} : {self.settings.relay_server_port}"
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
                    msg = f"Connected to connector from: {addr[0]}:{addr[1]}"
                    self.connected.emit()
                    logging.debug(f'{self.name}: {msg}')
                    while not self._shutdown.is_set():
                        self._pause.wait()
                        try:
                            # Wait for data
                            data = self.connection.recv(1024)
                            if data is not None and len(data) > 0:
                                logging.debug(f'{self.name}: connector received data: {data.decode()}')
                                if self.gspro_connection.connected():
                                    try:
                                        msg = self.gspro_connection.send_msg(data)
                                        self.send_msg(msg)
                                        self.relay_server_shot.emit(data)
                                        logging.debug(f'{self.name}: connector sent data to GSPro result: {msg.decode()}')
                                    except Exception as e:
                                        logging.debug(
                                            f'Error when trying to send shot to GSPro, process {self.name}: {format(e)}, {traceback.format_exc()}')
                                        self.shot_error.emit((e, traceback.format_exc()))
                            else:
                                self.disconnected.emit()
                                break
                        except socket.timeout:
                            pass
                        except ConnectionError:
                            logging.debug(f'{self.name}: connector disconnected')
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
                    self.connection.sendall(payload)
                except Exception as e:
                    msg = f"Relay server unknown error when trying to send result, Exception: {format(e)}"
                    logging.debug(msg)
                    raise Exception(msg)

    def shutdown(self):
        super().shutdown()
        if self.connection:
            self.connection.close()

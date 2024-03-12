import socket
import logging
import json
from threading import Event

import select
from PySide6.QtCore import QObject

from src.ball_data import BallData
from src.custom_exception import GSProConnectionTimeout, GSProConnectionUknownError, \
    GSProConnectionGSProClosedConnection, GSProConnectionSocketError


class GSProConnect(QObject):

    successful_send = 200

    def __init__(self, device_id, units, api_version) -> None:
        self._socket = None
        self._device_id = device_id
        self._units = units
        self._api_version = api_version
        self._shot_number = 1
        self._connected = False
        super(GSProConnect, self).__init__()

    def init_socket(self, ip_address: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_address, port))
        self._socket.settimeout(2)
        self._connected = True

    def connected(self):
        return self._connected

    def send_msg(self, payload, attempts=2):
        if self._connected:
            for attempt in range(attempts):
                try:
                    logging.info(f"Sending to GSPro data: {payload}")
                    self._socket.sendall(payload)
                    msg = self._socket.recv(2048)
                except socket.timeout:
                    logging.info('Timed out. Retrying...')
                    if attempt >= attempts-1:
                        raise GSProConnectionTimeout(f'Failed to send shot to GSPro after {attempts} attempts.')
                    Event().wait(0.5)
                    continue
                except socket.error as e:
                    msg = f'GSPro Connector socket error when trying to send shot, Exception: {format(e)}'
                    logging.debug(msg)
                    raise GSProConnectionSocketError(msg)
                except Exception as e:
                    msg = f"GSPro Connector unknown error when trying to send shot, Exception: {format(e)}"
                    logging.debug(msg)
                    raise GSProConnectionUknownError(msg)
                else:
                    if len(msg) == 0:
                        msg = f"GSPro closed the connection"
                        logging.debug(msg)
                        raise GSProConnectionGSProClosedConnection(msg)
                    else:
                        logging.debug(f"Response from GSPro: {msg}")
                        return msg

    def launch_ball(self, ball_data: BallData) -> None:
        if self._connected:
            device = {
                "DeviceID": self._device_id,
                "Units": self._units,
                "ShotNumber": self._shot_number,
                "APIversion": self._api_version
            }
            payload = device | ball_data.to_gspro()
            logging.debug(f'Launch Ball payload: {payload} ball_data.to_gspro(): {ball_data.to_gspro()}')
            self.send_msg(json.dumps(payload).encode("utf-8"))
            self._shot_number += 1

    def check_for_message(self):
        message = bytes(0)
        if self._connected:
            read_socket, write_socket, error_socket = select.select([self._socket], [], [], 0)
            while read_socket:
                message = message + self._socket.recv(1024)
                read_socket, write_socket, error_socket = select.select([self._socket], [], [], 0)
        return message

    def terminate_session(self):
        if self._socket:
            self._socket.close()
            self._connected = False

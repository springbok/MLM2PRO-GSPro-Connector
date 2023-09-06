import math
import socket
import logging
import json
from threading import Event
from src.ball_data import BallData
from src.custom_exception import GSProConnectionTimeout, GSProConnectionUknownError, \
    GSProConnectionGSProClosedConnection, GSProConnectionSocketError


class GSProConnect:
    def __init__(self, device_id, units, api_version) -> None:
        self._device_id = device_id
        self._units = units
        self._api_version = api_version
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._shot_number = 1
        self._connected = False

    def init_socket(self, ip_address: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ip_address, port))
        self._socket.settimeout(2)
        self._connected = True

    def send_msg(self, payload, attempts=2):
        for attempt in range(attempts):
            try:
                logging.info(f"Sending to GSPro data: {payload}")
                self._socket.sendall(json.dumps(payload).encode("utf-8"))
                msg = self._socket.recv(8096)
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
                    logging.debug(f"Response from GSPro: {msg.decode('UTF-8')}")

    def test_shot_data(self):
        ball_data = BallData()
        ball_data.speed = 85
        ball_data.spin_axis = 6.2
        ball_data.total_spin = 4743.0
        ball_data.hla = 1.0
        ball_data.vla = 20.9
        ball_data.club_speed = 65.0
        ball_data.back_spin = round(ball_data.total_spin * math.cos(math.radians(ball_data.spin_axis)))
        ball_data.side_spin = round(ball_data.total_spin * math.sin(math.radians(ball_data.spin_axis)))
        return ball_data

    def send_test_signal(self):
        ball_data = self.test_shot_data()
        self.launch_ball(ball_data)

    def launch_ball(self, ball_data: BallData) -> None:
        payload = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "BallData": {
                "Speed": ball_data.speed,
                "SpinAxis": ball_data.spin_axis,
                "TotalSpin": ball_data.total_spin,
                "HLA": ball_data.hla,
                "VLA": ball_data.vla,
                "Backspin": ball_data.back_spin,
                "SideSpin": ball_data.side_spin
            },
            "ClubData": {
                "Speed": ball_data.club_speed
            },
            "ShotDataOptions": {
                "ContainsBallData": True,
                "ContainsClubData": True,
                "LaunchMonitorIsReady": True,
                "LaunchMonitorBallDetected": True,
                "IsHeartBeat": False
            }
        }
        self.send_msg(payload)
        self._shot_number += 1

    def terminate_session(self):
        if self._socket:
            self._socket.close()
            self._connected = False

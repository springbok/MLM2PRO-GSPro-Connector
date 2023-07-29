import socket
import logging
import json
from time import sleep
from src.ball_data import BallData
from src.ui import UI, Color


class GSProConnect:
    def __init__(self, device_id, units, api_version, ip_address, port) -> None:
        self._device_id = device_id
        self._units = units
        self._api_version = api_version
        self.ip_address = ip_address
        self.port = port

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._shot_number = 1

    def init_socket(self):
        logging.info(f"Connecting to GSPro using IP: {self.ip_address} Port: {self.port}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.ip_address, self.port))
        self._socket.settimeout(5)

    def send_msg(self, payload, attempts=10):
        for attempt in range(attempts):
            try:
                logging.info(f"Sending to GSPro data: {payload}")
                self._socket.sendall(json.dumps(payload).encode("utf-8"))
                msg = self._socket.recv(8096)
            except socket.timeout as e:
                UI.display_message(Color.RED, "CONNECTOR ||", 'Timed out. Retrying...')
                sleep(1)
                continue
            except socket.error as e:
                UI.display_message(Color.RED, "CONNECTOR ||", f"Error waiting for GSPro response:{e}")
                raise
            else:
                if len(msg) == 0:
                    UI.display_message(Color.RED, "CONNECTOR ||", f"GSPro closed the connection")
                    return False
                else:
                    logging.debug(f"Response from GSPro: {msg.decode('UTF-8')}")
                    return True
        return False

    def send_test_signal(self):
        payload = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": 1,
            "APIversion": self._api_version,
            "BallData": {
                "Speed": 85.0,
                "SpinAxis": 6.2,
                "TotalSpin": 4743.0,
                "HLA": 1.0,
                "VLA": 20.9
            },
            "ClubData": {
                "Speed": 65.0
            },
            "ShotDataOptions": {
                "ContainsBallData": True,
                "ContainsClubData": True,
                "LaunchMonitorIsReady": True,
                "LaunchMonitorBallDetected": True,
                "IsHeartBeat": False
            }
        }

        resp = self.send_msg(payload)
        if (resp):
            UI.display_message(Color.RED, "CONNECTOR ||", 'GSPro Connected')
        else:
            raise ConnectionError("No response received from GSPro")

    def launch_ball(self, ball_data: BallData) -> None:
        api_data = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "BallData": {
                "Speed": ball_data.ballspeed,
                "SpinAxis": ball_data.spinaxis,
                "TotalSpin": ball_data.totalspin,
                "HLA": ball_data.hla,
                "VLA": ball_data.vla,
                "BackSpin": ball_data.back_spin,
                "SideSpin": ball_data.side_spin
            },
            "ShotDataOptions": {
                "ContainsBallData": True,
                "ContainsClubData": False
            },
        }

        print(json.dumps(api_data, indent=4))

        self.send_msg(api_data)

        self._shot_number += 1

    def terminate_session(self):
        if (self._socket):
            self._socket.close()
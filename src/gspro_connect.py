import math
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
            except socket.timeout:
                UI.display_message(Color.RED, "CONNECTOR ||", 'Timed out. Retrying...')
                sleep(1)
                continue
            except socket.error as e:
                UI.display_message(Color.RED, "CONNECTOR ||", f"Error waiting for GSPro response:{format(e)}")
                raise
            except Exception as e:
                if "[WinError 10054]" in format(e):
                    msg = f"Could not connect to the GSPro Connect, please start/restart from GSPro:{format(e)}"
                else:
                    msg = f"Unknown error: format(e)"
                UI.display_message(Color.RED, "CONNECTOR ||", msg)
                raise
            else:
                if len(msg) == 0:
                    UI.display_message(Color.RED, "CONNECTOR ||", f"GSPro closed the connection")
                    return False
                else:
                    logging.debug(f"Response from GSPro: {msg.decode('UTF-8')}")
                    return True
        return False

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
        UI.display_message(Color.GREEN, "CONNECTOR ||", f"Success: {ball_data.to_json()}")

        self._shot_number += 1

    def terminate_session(self):
        if self._socket:
            self._socket.close()
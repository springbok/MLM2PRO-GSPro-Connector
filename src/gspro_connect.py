import socket
import logging
import json
from time import sleep
from src.ball_data import BallData

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
        self._socket.connect((self.ip_address, self.port))
        self._socket.settimeout(2)

    def send_msg(self, payload, attempts=10):
        for attempt in range(attempts):
            try:
                logging.info("sending message to GSPro...")
                self._socket.sendall(json.dumps(payload).encode("utf-8"))
                msg = self._socket.recv(8096)
            except socket.timeout as e:
                print('timed out. Retrying...')
                sleep(1)
                continue
            except socket.error as e:
                print('Error waiting for GSPro response:')
                print(e)
                raise
            else:
                if len(msg) == 0:
                    print('GS Pro closed connection')
                    return False
                else:
                    print("response from GSPro: ")
                    print(msg.decode('UTF-8'))
                    return True
        print('passed loop')
        return False

    def send_test_signal(self):
        payload = {
            "DeviceID": self._device_id,
            "Units": self._units,
            "ShotNumber": self._shot_number,
            "APIversion": self._api_version,
            "ShotDataOptions": {
                "ContainsBallData": False,
                "ContainsClubData": False,
            },
        }

        resp = self.send_msg(payload)
        if (resp):
            print('GSPro Connected...')
        else:
            raise Exception

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
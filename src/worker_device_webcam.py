import functools
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from PySide6.QtCore import QObject, Signal
from src.ball_data import BallData, PuttType
from src.custom_exception import PutterNotSelected
from src.putting_settings import PuttingSettings
from src.worker_base import WorkerBase


class PuttingRequestHandler(QObject, BaseHTTPRequestHandler):

    def __init__(self, *args, putting_worker=None, **kwargs):
        self.ball_data = None
        self.putting_worker = putting_worker
        super(BaseHTTPRequestHandler, self).__init__(*args, **kwargs)

    def do_POST(self):
        message = ''
        error = False
        self.ball_data = BallData()
        logging.debug('do_POST')
        content_len = int(self.headers.get('content-length', 0))
        try:
            if content_len <= 0:
                raise ValueError('Invalid putt data')
            if not self.putting_worker.putter_selected():
                raise PutterNotSelected('Putter not selected in GSPro, ignoring.')
            post_body = self.rfile.read(content_len)
            putt_data = json.loads(post_body)
            self.ball_data.speed = float(putt_data['ballData']['BallSpeed'])
            self.ball_data.total_spin = float(putt_data['ballData']['TotalSpin'])
            self.ball_data.hla = float(putt_data['ballData']['LaunchDirection'])
            self.ball_data.putt_type = PuttType.WEBCAM
            self.ball_data.good_shot = True
            self.ball_data.club = 'PT'
            message = {"result": "Success"}
            logging.debug(f'Putting Server putt received: {self.ball_data.to_json()}')
        except Exception as e:
            message = {"result": format(e)}
            logging.debug(f'Putting Error: {format(e)}')
            self.putting_worker.send_error(e)
            error = True
        finally:
            logging.debug("Send 200 response")
            self.send_response_only(200)
            self.end_headers()
            self.wfile.write(str.encode(json.dumps(message)))
            if not error:
                self.putting_worker.send_putt(self.ball_data)


class WorkerDeviceWebcam(WorkerBase):
    shot = Signal(object or None)

    def __init__(self, settings: PuttingSettings):
        super(WorkerDeviceWebcam, self).__init__()
        self._server = None
        self.putter = False
        self.settings = settings
        self.name = 'WorkerDeviceWebcam'

    def run(self):
        self.started.emit()
        logging.debug(f'{self.name} Started')
        handler_partial = functools.partial(PuttingRequestHandler, putting_worker=self)
        self._server = HTTPServer(
            (self.settings.webcam['ip_address'], self.settings.webcam['port']),
            handler_partial)
        self._server.serve_forever()

    def shutdown(self):
        super().shutdown()
        if self._server is not None:
            self._server.shutdown()
            self._server.socket.close()
            self._server = None

    def send_putt(self, putt):
        self.shot.emit(putt)

    def send_error(self, error):
        self.error.emit(error)

#!/usr/bin/env python3
"""
ExPutt putt data capture — quiet mode for orientation / setup testing.

Connects like the phone app, arms practice, then prints ball/club data
each time a putt is measured. Sync/preview noise is suppressed.

  python exputt_client.py
  python exputt_client.py --ip 192.168.x.x
  python exputt_client.py --log my_session.log
  python exputt_client.py --verbose   # show all protocol traffic

Every line is timestamped and written to both the console and a logfile
(default: exputt_YYYYMMDD_HHMMSS.log).

Requires: pip install pyzmq
Close the phone ExPutt app first (camera allows one peer only).
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO

UDP_DISCOVERY_PORT = 9999
NETMQ_PORT = 8889

COMMENT_FAIL_TRY_JOINING = "FAIL_TRY_JOINING:"
COMMENT_RESYNC = "resyncToMat"
COMMENT_STOP_IMAGE = "stopSendImage"
COMMENT_MATCH_BEGIN = "PM_API_MatchBegin"
COMMENT_MATCH_ENDED = "PM_API_MatchEnded"
COMMENT_DEX_RIGHT = "setDexterityRight"
COMMENT_DEX_LEFT = "setDexterityLeft"

PUTT_READY_RETRY_SEC = 8.0
PUTT_READY_MAX_RETRIES = 3

zmq = None
_logger: Optional["SessionLogger"] = None


def _require_zmq():
    global zmq
    if zmq is None:
        try:
            import zmq as _zmq
        except ImportError as exc:
            raise SystemExit("Missing dependency: pip install pyzmq") from exc
        zmq = _zmq
    return zmq


class SessionLogger:
    """Write the same timestamped line to console and a logfile."""

    def __init__(self, path: Path):
        self.path = path
        self._fp: TextIO = path.open("a", encoding="utf-8", newline="\n")
        self.log(f"=== log started -> {path.resolve()} ===")

    def log(self, msg: str = "", *, also_stderr: bool = False) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f"[{ts}] {msg}" if msg else f"[{ts}]"
        stream = sys.stderr if also_stderr else sys.stdout
        print(line, file=stream, flush=True)
        self._fp.write(line + "\n")
        self._fp.flush()

    def close(self) -> None:
        try:
            self.log("=== log ended ===")
            self._fp.close()
        except Exception:
            pass


def log(msg: str = "", *, also_stderr: bool = False) -> None:
    if _logger is not None:
        _logger.log(msg, also_stderr=also_stderr)
    else:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        stream = sys.stderr if also_stderr else sys.stdout
        print(f"[{ts}] {msg}" if msg else f"[{ts}]", file=stream, flush=True)


@dataclass
class ShotInfo:
    angle: float
    speed: float


@dataclass
class ClubInfo:
    time: float
    speed: float
    putter_direction: float
    impact_angle: float
    putter_x: list[float]
    putter_y: list[float]
    putter_angle: list[float]
    putter_pos: float


@dataclass
class PuttResult:
    shot: ShotInfo
    club: ClubInfo
    raw: str = ""


@dataclass
class BroadcastMessage:
    server_uuid: str = ""
    ip_address: str = ""
    app_version: str = ""
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, text: str) -> "BroadcastMessage":
        data = json.loads(text)
        return cls(
            server_uuid=str(data.get("_serverUUID", "")),
            ip_address=str(data.get("_ipAddress", "")),
            app_version=str(data.get("_appVersion", "")),
            raw=data,
        )


def discover_camera(timeout: float = 30.0, verbose: bool = False) -> BroadcastMessage:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except (AttributeError, OSError):
        pass
    sock.bind(("", UDP_DISCOVERY_PORT))
    sock.settimeout(1.0)

    log(f"Looking for camera on UDP :{UDP_DISCOVERY_PORT} ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            payload, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue

        text = payload.decode("ascii", errors="replace").strip("\x00").strip()
        if verbose:
            log(f"[discover] {addr[0]}: {text[:200]}")
        if "_ipAddress" not in text:
            continue
        try:
            msg = BroadcastMessage.from_json(text)
        except json.JSONDecodeError:
            continue
        if not msg.ip_address:
            continue

        log(f"Found camera {msg.ip_address} (v{msg.app_version})")
        sock.close()
        return msg

    sock.close()
    raise TimeoutError(f"no camera on UDP :{UDP_DISCOVERY_PORT} within {timeout:.0f}s")


def make_node(packet_id: str, comment: str = "", request_packet_id: str = "") -> dict:
    node = {
        "PacketID": packet_id,
        "RequestPacketID": request_packet_id or None,
        "DataInfo": None,
        "Comment": comment if comment != "" else None,
    }
    return {k: v for k, v in node.items() if v is not None}


def parse_putt_result(comment: str) -> PuttResult:
    parts = comment.split(",")
    if not parts or parts[0] != "PuttResult":
        raise ValueError(f"not a PuttResult comment: {comment!r}")
    if len(parts) < 17:
        raise ValueError(f"PuttResult CSV too short ({len(parts)} fields): {comment!r}")

    vals = [float(p) for p in parts[1:17]]
    return PuttResult(
        shot=ShotInfo(angle=vals[0], speed=vals[1]),
        club=ClubInfo(
            time=vals[2],
            speed=vals[3],
            putter_direction=vals[4],
            impact_angle=vals[5],
            putter_x=vals[6:9],
            putter_y=vals[9:12],
            putter_angle=vals[12:15],
            putter_pos=vals[15],
        ),
        raw=comment,
    )


def display_putt(result: PuttResult, putt_num: int) -> None:
    s, c = result.shot, result.club
    log("")
    log("=" * 60)
    log(f"PUTT #{putt_num}")
    log("=" * 60)
    log("ball / shot")
    log(f"  angle : {s.angle}")
    log(f"  speed : {s.speed}")
    log("club / putter")
    log(f"  time             : {c.time}")
    log(f"  speed            : {c.speed}")
    log(f"  putter_direction : {c.putter_direction}")
    log(f"  impact_angle     : {c.impact_angle}")
    log(f"  putter_x         : {c.putter_x}")
    log(f"  putter_y         : {c.putter_y}")
    log(f"  putter_angle     : {c.putter_angle}")
    log(f"  putter_pos       : {c.putter_pos}")
    log("-" * 60)
    log(f"raw: {result.raw}")
    log("=" * 60)
    log("")


class ExPuttClient:
    def __init__(self, ip: str, port: int = NETMQ_PORT, verbose: bool = False):
        z = _require_zmq()
        self.ip = ip
        self.port = port
        self.verbose = verbose
        self.endpoint = f"tcp://{ip}:{port}"
        self.ctx = z.Context.instance()
        self.sock = self.ctx.socket(z.DEALER)
        self.sock.setsockopt(z.LINGER, 0)
        self.sock.setsockopt(z.RCVTIMEO, 500)
        self.sock.setsockopt(z.SNDTIMEO, 2000)
        self.running = False
        self.session_ok = False
        self.mat_ok = False
        self.synced = False
        self.armed = False
        self.putt_ready_count = 0
        self.putt_count = 0
        self.dexterity = COMMENT_DEX_RIGHT
        self._last_alive = 0.0
        self._armed_at = 0.0
        self._match_begin_retries = 0
        self._status = ""

    def _status_log(self, msg: str) -> None:
        if self.verbose:
            log(msg)
        elif msg != self._status:
            # Deduplicate quiet status lines on screen/file.
            self._status = msg
            log(msg)

    def connect_socket(self) -> None:
        log(f"Connecting to {self.endpoint}")
        log("Close the phone ExPutt app first (one peer only).")
        self.sock.connect(self.endpoint)
        self.running = True

    def send(self, packet_id: str, comment: str = "", request_packet_id: str = "") -> None:
        node = make_node(packet_id.upper(), comment=comment, request_packet_id=request_packet_id)
        payload = json.dumps(node, separators=(",", ":"))
        self.sock.send_string(payload)
        if self.verbose:
            log(f"[send] {payload}")

    def send_test(self, comment: str) -> None:
        self.send("N_TEST", comment=comment)

    def maybe_alive(self, interval: float = 1.0) -> None:
        if not self.session_ok:
            return
        now = time.time()
        if now - self._last_alive >= interval:
            # Keepalive without flooding the console.
            node = make_node("N_ALIVE")
            self.sock.send_string(json.dumps(node, separators=(",", ":")))
            self._last_alive = now

    def recv_node(self) -> Optional[dict]:
        z = _require_zmq()
        try:
            frames = self.sock.recv_multipart()
        except z.Again:
            return None

        text = None
        for frame in frames:
            if not frame:
                continue
            try:
                text = frame.decode("utf-8")
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            return None

        if self.verbose:
            preview = text if len(text) <= 300 else f"{text[:120]}...({len(text)} chars)..."
            log(f"[recv] {preview}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def handshake(self, timeout: float = 15.0) -> bool:
        self._status_log("Handshaking...")
        self.send("N_VERIFY_ID")
        deadline = time.time() + timeout
        while time.time() < deadline:
            node = self.recv_node()
            if node is None:
                continue
            packet_id = str(node.get("PacketID") or "")
            if packet_id == "N_BUSY":
                log("Camera busy - close the phone app and retry.")
                return False
            if packet_id == "N_OK":
                self.session_ok = True
                self.send("N_REQ_CONNECT", comment=COMMENT_FAIL_TRY_JOINING)
                time.sleep(0.1)
                self.send_test(COMMENT_RESYNC)
                self._status_log("Syncing mat... place/aim the camera until MatOK")
                return True
            self.handle_node(node)
        log(f"Timed out waiting for N_OK ({timeout:.0f}s)")
        return False

    def accept_sync_and_arm(self) -> None:
        if not self.synced:
            self.send_test(COMMENT_STOP_IMAGE)
            self.synced = True
            time.sleep(0.2)
            self.send_test(self.dexterity)
            time.sleep(0.15)
        if not self.armed:
            self._send_match_begin()

    def _send_match_begin(self) -> None:
        self.send_test(COMMENT_MATCH_BEGIN)
        self.armed = True
        self._armed_at = time.time()
        self._status_log("Armed - putt when ready (ball/club data prints each putt)")

    def maybe_rearm_for_putt_ready(self) -> None:
        if not self.armed or self.putt_ready_count > 0:
            return
        if self._match_begin_retries >= PUTT_READY_MAX_RETRIES:
            return
        if time.time() - self._armed_at < PUTT_READY_RETRY_SEC:
            return
        self._match_begin_retries += 1
        if self.verbose:
            log(f"[practice] retry MatchBegin ({self._match_begin_retries})")
        self._send_match_begin()

    def handle_node(self, node: dict) -> Optional[PuttResult]:
        packet_id = str(node.get("PacketID") or node.get("packetID") or "")
        comment = node.get("Comment") or node.get("comment") or ""
        if comment is None:
            comment = ""
        comment = str(comment)

        if packet_id == "N_BUSY":
            log("Camera busy (N_BUSY).")
            self.running = False
            return None
        if packet_id == "N_OK":
            if not self.session_ok:
                self.session_ok = True
                self.send("N_REQ_CONNECT", comment=COMMENT_FAIL_TRY_JOINING)
                self.send_test(COMMENT_RESYNC)
            return None
        if packet_id == "N_DISCONNECT":
            log("Disconnected.")
            self.running = False
            return None

        if packet_id == "N_FAIL" or comment.startswith("PuttResult"):
            if not comment:
                return None
            # JPEG mat preview — ignore quietly.
            if "," not in comment:
                return None

            event = comment.split(",", 1)[0]

            if event == "PuttResult":
                return parse_putt_result(comment)

            if event == "PuttReady":
                self.putt_ready_count += 1
                self._match_begin_retries = 0
                self._armed_at = time.time()
                log(f"[ready] ball in launch area (#{self.putt_ready_count})")
                if not self.armed:
                    self.accept_sync_and_arm()
                return None

            if event == "MatOK":
                self.mat_ok = True
                self._status_log("MatOK - arming practice")
                self.accept_sync_and_arm()
                return None

            if event == "FindMat":
                self._status_log("Looking for mat... adjust camera orientation")
                return None

            if self.verbose:
                log(f"[gameplay] {comment[:160]}")
            return None

        if self.verbose:
            log(f"[recv] unhandled PacketID={packet_id!r}")
        return None

    def run(self, duration: float = 0.0, alive: bool = True) -> int:
        end = time.time() + duration if duration > 0 else None
        log("Waiting for putts - Ctrl+C to stop")
        log("")
        try:
            while self.running:
                if end is not None and time.time() >= end:
                    break
                if alive:
                    self.maybe_alive()
                self.maybe_rearm_for_putt_ready()

                node = self.recv_node()
                if node is None:
                    continue
                result = self.handle_node(node)
                if result is not None:
                    self.putt_count += 1
                    display_putt(result, self.putt_count)
        except KeyboardInterrupt:
            log("")
            log("Stopped.")
        finally:
            if self.armed:
                try:
                    self.send_test(COMMENT_MATCH_ENDED)
                except Exception:
                    pass
            self.close()
        log(f"Done. putts={self.putt_count} ready_events={self.putt_ready_count}")
        return self.putt_count

    def close(self) -> None:
        self.running = False
        try:
            self.sock.close(0)
        except Exception:
            pass


def main() -> int:
    global _logger

    parser = argparse.ArgumentParser(
        description="Capture ExPutt ball/club data each putt (quiet by default)"
    )
    parser.add_argument("--ip", help="Skip discovery; connect to this camera IP")
    parser.add_argument("--port", type=int, default=NETMQ_PORT)
    parser.add_argument("--discover-timeout", type=float, default=30.0)
    parser.add_argument("--duration", type=float, default=0.0, help="Seconds to listen (0 = until Ctrl+C)")
    parser.add_argument("--no-alive", action="store_true")
    parser.add_argument("--left-handed", action="store_true")
    parser.add_argument(
        "--log",
        default="",
        help="Logfile path (default: exputt_YYYYMMDD_HHMMSS.log in cwd)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full protocol traffic (send/recv/images)",
    )
    parser.add_argument(
        "--demo-parse",
        action="store_true",
        help="Print a sample putt and exit (no network)",
    )
    args = parser.parse_args()

    log_path = Path(args.log) if args.log else Path(
        f"exputt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    _logger = SessionLogger(log_path)

    try:
        if args.demo_parse:
            sample = (
                "PuttResult,1.25,2.50,0.10,1.80,0.05,-0.20,"
                "100,110,120,200,210,220,1.1,1.2,1.3,0.5"
            )
            display_putt(parse_putt_result(sample), 1)
            return 0

        if args.ip:
            ip = args.ip
        else:
            try:
                broadcast = discover_camera(
                    timeout=args.discover_timeout, verbose=args.verbose
                )
            except TimeoutError as exc:
                log(f"error: {exc}", also_stderr=True)
                return 1
            ip = broadcast.ip_address

        z = _require_zmq()
        client = ExPuttClient(ip, port=args.port, verbose=args.verbose)
        client.dexterity = COMMENT_DEX_LEFT if args.left_handed else COMMENT_DEX_RIGHT
        try:
            client.connect_socket()
            if not client.handshake():
                client.close()
                return 2
        except z.ZMQError as exc:
            log(f"error connecting to {ip}:{args.port}: {exc}", also_stderr=True)
            return 1

        client.run(duration=args.duration, alive=not args.no_alive)
        return 0
    finally:
        if _logger is not None:
            _logger.close()
            _logger = None


if __name__ == "__main__":
    sys.exit(main())

import binascii
import math
import struct
from typing import List

from crcmod import crcmod


class BluetoothUtils:

    @staticmethod
    def bytearray_to_int_array(data: bytearray) -> List[int]:
        if not data:
            return []
        return [byte & 0xFF for byte in data]

    @staticmethod
    def bytes_to_int(byte_array: bytearray, is_little_endian: bool) -> int:
        if is_little_endian:
            return byte_array[0] | (byte_array[1] << 8) | (byte_array[2] << 16) | (byte_array[3] << 24)
        else:
            byte_array.reverse()  # Convert to big-endian if necessary
            return (byte_array[0] << 24) | (byte_array[1] << 16) | (byte_array[2] << 8) | byte_array[3]

    @staticmethod
    def get_air_pressure_bytes(d) -> bytearray:
        d2 = d * 0.0065
        value = (int((((math.pow(1.0 - (d2 / ((15.0 + d2) + 273.15)), 5.257) * 1013.25) * 0.1) - 50.0) * 1000.0))
        return BluetoothUtils.int_to_byte_array(value, True, True)

    @staticmethod
    def get_temperature_bytes(d) -> bytearray:
        value = int(d * 100.0)
        return BluetoothUtils.int_to_byte_array(value, True, True)

    @staticmethod
    def long_to_uint_to_byte_array(j, little_endian) -> bytes:
        format_string = '<Q' if little_endian else '>Q'
        return struct.pack(format_string, j)

    @staticmethod
    def byte_array_to_hex_string(b:bytearray) -> str:
        if b is None:
            return ''
        return ''.join('{:02X}'.format(b) for b in b)

    @staticmethod
    def int_to_byte_array(n, little_endian, as_short=False) -> bytearray:
        hex_value = hex(n)[2:]  # Convert to hex and remove '0x'
        hex_value = hex_value.zfill(8)  # Pad with zeros to ensure it's 4 bytes
        bytes_value = bytes.fromhex(hex_value)  # Convert hex to bytes
        format_string = '<I' if little_endian else '>I'
        value = struct.pack(format_string, n)
        if as_short:
            value = BluetoothUtils.int_byte_array_to_short_byte_array(value, little_endian)
        return value

    @staticmethod
    def int_byte_array_to_short_byte_array(int_byte_array, is_little_endian) -> bytearray:
        short_byte_array = bytearray()
        for i in range(0, len(int_byte_array), 4):
            int_bytes = int_byte_array[i:i+4]
            format_string = '<I' if is_little_endian else '>I'
            int_value = struct.unpack(format_string, int_bytes)[0]
            short_bytes = struct.pack('<H' if is_little_endian else '>H', int_value)
            short_byte_array.extend(short_bytes)
        return short_byte_array

    @staticmethod
    def checksum(data: bytearray) -> int:
        crc16_func = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        return crc16_func(data)

    def to_hex_string(data: bytearray) -> str:
        return binascii.hexlify(data).decode()

    def from_hex_string(hex_string: str) -> bytes:
        return binascii.unhexlify(hex_string)
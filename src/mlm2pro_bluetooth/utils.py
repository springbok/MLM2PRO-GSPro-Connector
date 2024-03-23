from typing import List


class MLM2PROUtils:

    @staticmethod
    def bytearray_to_int_array(data: bytearray, is_little_endian: bool=False) -> List[int]:
        if not data:
            return []
        return [byte & 0xFF for byte in data]

    @staticmethod
    def bytes_to_int(byte_array: bytearray, is_little_endian: bool):
        if is_little_endian:
            return byte_array[0] | (byte_array[1] << 8) | (byte_array[2] << 16) | (byte_array[3] << 24)
        else:
            byte_array.reverse()  # Convert to big-endian if necessary
            return (byte_array[0] << 24) | (byte_array[1] << 16) | (byte_array[2] << 8) | byte_array[3]
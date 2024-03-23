from typing import List


class MLM2PROUtils:

    @staticmethod
    def bytearray_to_int_array(data: bytearray) -> List[int]:
        return [byte & 0xFF for byte in data]
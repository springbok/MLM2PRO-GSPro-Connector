from typing import List


class MLM2PROUtils:

    @staticmethod
    def bytearray_to_int_array(data: bytearray) -> List[int]:
        if not data:
            return []
        return [byte & 0xFF for byte in data]
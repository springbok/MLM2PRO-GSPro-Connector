from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import logging


class MLM2PROEncryption:
    def __init__(self):
        self.iv_parameter = bytes([109, 46, 82, 19, 33, 50, 4, 69, 111, 44, 121, 72, 16, 101, 109, 66])
        self.predeterminedKey = bytes([26, 24, 1, 38, 249, 154, 60, 63, 149, 185, 205, 150, 126, 160, 38, 61, 89, 199, 68, 140, 255, 21, 250, 131, 55, 165, 121, 250, 49, 121, 233, 21])
        self.encryptionKey = self.predeterminedKey

    def get_encryption_type_bytes(self) -> bytes:
        return bytes([0, 1])

    def get_key_bytes(self) -> bytes:
        return self.encryptionKey

    def encrypt(self, input) -> bytes:
        if input is None:
            logging.error("Encrypt received null input")
            return bytes()
        cipher = AES.new(self.encryptionKey, AES.MODE_CBC, self.iv_parameter)
        ct_bytes = cipher.encrypt(pad(input, AES.block_size))
        return ct_bytes

    def decrypt(self, input: bytes) -> bytes or None:
        if input is None:
            logging.error("Decrypt received null input")
            return None
        try:
            cipher = AES.new(self.encryptionKey, AES.MODE_CBC, self.iv_parameter)
            pt = unpad(cipher.decrypt(input), AES.block_size)
            return pt
        except Exception as ex:
            logging.error(f"Error decrypting data: {str(ex)}")
            return None

    def decrypt_known_key(self, input, encryption_keyinput) -> bytes or None:
        try:
            cipher = AES.new(encryption_keyinput, AES.MODE_CBC, self.iv_parameter)
            pt = unpad(cipher.decrypt(input), AES.block_size)
            return pt
        except Exception as ex:
            logging.error(f"Error decrypting data: {str(ex)}")
            return None
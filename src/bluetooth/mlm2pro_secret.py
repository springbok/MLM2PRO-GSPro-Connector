from src.bluetooth.password_encryption import PasswordEncryption


class MLM2PROSecret:
    WEBAPI_SECRET = "d3d4baff-02c7-4c91-8100-2e362936e06e"
    ENCRYPT_PASSWORD = "Ups!240v2701"

    @staticmethod
    def encrypt():
        return PasswordEncryption.encode_secret(MLM2PROSecret.WEBAPI_SECRET, MLM2PROSecret.ENCRYPT_PASSWORD)

    @staticmethod
    def decrypt(data):
        return PasswordEncryption.decode_secret(data, MLM2PROSecret.ENCRYPT_PASSWORD)

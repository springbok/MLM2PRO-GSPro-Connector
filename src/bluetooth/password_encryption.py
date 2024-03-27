import binascii

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class PasswordEncryption:

  @staticmethod
  def get_key(password, salt=None):
    if salt is None:
      salt = get_random_bytes(AES.block_size)
    key = PBKDF2(password, salt, dkLen=32)  # AES key must be either 16, 24, or 32 bytes long
    return salt, key

  @staticmethod
  def encrypt(data, password):
    salt, key = PasswordEncryption.get_key(password)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return salt + cipher.iv + ct_bytes

  @staticmethod
  def decrypt(ct, password):
    salt = ct[:AES.block_size]
    key = PasswordEncryption.get_key(password, salt)[1]
    iv = ct[AES.block_size:2 * AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct[2 * AES.block_size:]), AES.block_size)
    return pt.decode()

  @staticmethod
  def encode_secret(data, password):
    bytes = PasswordEncryption.encrypt(data, password)
    return binascii.hexlify(bytes).decode()

  @staticmethod
  def decode_secret(data, password):
    bytes = binascii.unhexlify(data)
    return PasswordEncryption.decrypt(bytes, password)
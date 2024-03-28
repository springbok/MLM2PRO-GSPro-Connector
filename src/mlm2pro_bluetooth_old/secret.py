import binascii

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class MLM2PROSecret:
  WEBAPI_SECRET = "d3d4baff-02c7-4c91-8100-2e362936e06e"
  ENCRYPT_PASSWORD = "Ups!240v2701"

  @staticmethod
  def get_key(password, salt=None):
    if salt is None:
      salt = get_random_bytes(AES.block_size)
    key = PBKDF2(password, salt, dkLen=32)  # AES key must be either 16, 24, or 32 bytes long
    return salt, key

  @staticmethod
  def encrypt(data, password):
    salt, key = MLM2PROSecret.get_key(password)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return salt + cipher.iv + ct_bytes

  @staticmethod
  def decrypt(ct, password):
    salt = ct[:AES.block_size]
    key = MLM2PROSecret.get_key(password, salt)[1]
    iv = ct[AES.block_size:2 * AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct[2 * AES.block_size:]), AES.block_size)
    return pt.decode()

  @staticmethod
  def encode_secret():
    bytes = MLM2PROSecret.encrypt(MLM2PROSecret.WEBAPI_SECRET, MLM2PROSecret.ENCRYPT_PASSWORD)
    return binascii.hexlify(bytes).decode()

  @staticmethod
  def decode_secret(data):
    bytes = binascii.unhexlify(data)
    return MLM2PROSecret.decrypt(bytes, MLM2PROSecret.ENCRYPT_PASSWORD)
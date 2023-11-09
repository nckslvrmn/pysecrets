import os

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from .helpers import rand_string


class SimpleCrypt:
    def __init__(self, secret_id=None, data=None, passphrase=None, nonce=None, salt=None, header=None):
        self.secret_id = secret_id or rand_string(16)
        self.data = data or None
        self.passphrase = passphrase or rand_string(32, url_safe=False)
        self.nonce = nonce or os.urandom(96)
        self.salt = salt or os.urandom(16)
        self.header = header or os.urandom(16)

    def encrypt(self, input_data):
        cipher = self.__init_cipher()
        to_enc = input_data.encode('utf-8') if isinstance(input_data, str) else input_data
        self.data = cipher.encrypt(self.nonce, to_enc, self.header)

    def decrypt(self):
        cipher = self.__init_cipher()
        try:
            return cipher.decrypt(self.nonce, self.data, self.header)
        except InvalidTag:
            return None

    def __init_cipher(self):
        scrypt = Scrypt(self.salt, length=32, n=2**14, r=8, p=1)
        key = scrypt.derive(bytes(self.passphrase, encoding='utf8'))
        cipher = AESGCM(key)
        return cipher

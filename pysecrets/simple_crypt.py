from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes
from .helpers import rand_string


class SimpleCrypt:
    def __init__(self, secret_id=None, data=None, password=None, nonce=None, salt=None, tag=None, header=None):
        self.secret_id = secret_id or rand_string(16)
        self.data = data or None
        self.password = password or rand_string(32, url_safe=False)
        self.nonce = nonce or get_random_bytes(16)
        self.salt = salt or get_random_bytes(16)
        self.tag = tag or None
        self.header = header or get_random_bytes(16)

    def encrypt(self, input_data):
        cipher = self.__init_cipher()
        to_enc = input_data.encode('utf-8') if isinstance(input_data, str) else input_data
        self.data, self.tag = cipher.encrypt_and_digest(to_enc)

    def decrypt(self):
        cipher = self.__init_cipher()
        return cipher.decrypt_and_verify(self.data, self.tag)

    def __init_cipher(self):
        key = scrypt(self.password, self.salt, 32, N=2**14, r=8, p=1)
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        cipher.update(self.header)
        return cipher

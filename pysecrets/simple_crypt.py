from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes
from .helpers import rand_string


class SimpleCrypt:
    def __init__(self, secret_id=None, data=None, password=None, nonce=None, salt=None, tag=None, header=None):
        self.secret_id = rand_string(16) if secret_id is None else secret_id
        self.data = None if data is None else data
        self.password = rand_string(32, url_safe=False) if password is None else password
        self.nonce = get_random_bytes(16) if nonce is None else nonce
        self.salt = get_random_bytes(16) if salt is None else salt
        self.tag = None if tag is None else tag
        self.header = get_random_bytes(16) if header is None else header

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

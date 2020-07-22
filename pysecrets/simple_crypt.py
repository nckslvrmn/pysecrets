from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes
from .helpers import rand_string, b64d
import json

class SimpleCrypt:
    def __init__(self, secret_id=None, data=None, password=None, nonce=None, salt=None, tag=None, header=None):
        self.secret_id = rand_string(16) if secret_id == None else secret_id
        self.data = None if data == None else data
        self.password = rand_string(32, url_safe=False) if password == None else password
        self.nonce = get_random_bytes(16) if nonce == None else nonce
        self.salt = get_random_bytes(16) if salt == None else salt
        self.tag = None if tag == None else tag
        self.header = get_random_bytes(16) if header == None else header

    @classmethod
    def from_json(self, secret_json):
        data = json.loads(secret_json)
        return SimpleCrypt(
            secret_id=data['secret_id'],
            data=b64d(data['data']),
            nonce=b64d(data['nonce']),
            salt=b64d(data['salt']),
            tag=b64d(data['tag']),
            header=b64d(data['header'])
        )

    def encrypt(self, input_data):
        cipher = self.__init_cipher()
        self.data, self.tag = cipher.encrypt_and_digest(input_data.encode('utf-8'))

    def decrypt(self):
        cipher = self.__init_cipher()
        return cipher.decrypt_and_verify(self.data, self.tag)

    def __init_cipher(self):
        key = scrypt(self.password, self.salt, 32, N=2**14, r=8, p=1)
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        cipher.update(self.header)
        return cipher

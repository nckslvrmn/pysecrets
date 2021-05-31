import os

from pysecrets.simple_crypt import SimpleCrypt
import unittest


class TestSimpleCrypt(unittest.TestCase):
    def test_simple_crypt_string(self):
        secret = SimpleCrypt()
        data = 'secret text'
        secret.encrypt(data)
        decrypted = secret.decrypt()
        self.assertEqual(data, decrypted.decode('utf-8'))

    def test_simple_crypt_file(self):
        secret = SimpleCrypt()
        file = open(os.path.join(os.path.dirname(__file__), 'test.txt'))
        data = file.read()
        file.close()
        secret.encrypt(data)
        decrypted = secret.decrypt()
        self.assertEqual(data, decrypted.decode('utf-8'))

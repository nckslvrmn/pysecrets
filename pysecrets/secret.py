import boto3
import os
import time
from .simple_crypt import SimpleCrypt
from .helpers import b64s

class Secret:
    def __init__(self, data, view_count):
        self.data = data
        self.view_count = view_count

    def encrypt(self):
        sc = SimpleCrypt()
        sc.encrypt(self.data)
        self.crypt = sc
        return sc.secret_id, sc.password

    def store(self):
        ttl = int(time.time() + (86400 * int(os.environ.get('TTL_DAYS', 5))))
        dynamo = boto3.client('dynamodb', region_name = 'us-east-1')
        resp = dynamo.put_item(
            TableName = 'Secrets',
            Item = {
                'secret_id': { 'S': self.crypt.secret_id },
                'data': { 'S': b64s(self.crypt.data) },
                'nonce': { 'S': b64s(self.crypt.nonce) },
                'salt': { 'S': b64s(self.crypt.salt) },
                'tag': { 'S': b64s(self.crypt.tag) },
                'header': { 'S': b64s(self.crypt.header) },
                'ttl': { 'N': str(ttl) },
                'view_count': { 'N': str(self.view_count) }
            }
        )

import boto3
import os
import time
from .simple_crypt import SimpleCrypt
from .helpers import b64s, b64d

class Secret:
    def __init__(self, data=None, view_count=1, secret_id=None):
        self.data = data
        self.view_count = view_count
        self.secret_id = secret_id

    def encrypt(self):
        sc = SimpleCrypt()
        sc.encrypt(self.data)
        self.crypt = sc
        return sc.secret_id, sc.password

    def decrypt(self, password):
        self.crypt.password = password
        decrypted = self.crypt.decrypt()
        self.__burn()
        return decrypted.decode('utf-8')

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

    @classmethod
    def load(self, secret_id):
        dynamo = boto3.client('dynamodb', region_name = 'us-east-1')
        try:
            resp = dynamo.get_item(
                TableName = 'Secrets',
                Key = { 'secret_id': { 'S': secret_id } }
            )
        except ResourceNotFoundException:
            return None
        if resp.get('Item') == None:
            return None
        sec = Secret(
            secret_id=resp['Item']['secret_id']['S'],
            view_count=int(resp['Item']['view_count']['N'])
        )
        sec.crypt = SimpleCrypt(
            secret_id=resp['Item']['secret_id']['S'],
            data=b64d(resp['Item']['data']['S']),
            nonce=b64d(resp['Item']['nonce']['S']),
            salt=b64d(resp['Item']['salt']['S']),
            tag=b64d(resp['Item']['tag']['S']),
            header=b64d(resp['Item']['header']['S'])
        )
        return sec

    def __burn(self):
        dynamo = boto3.client('dynamodb', region_name = 'us-east-1')
        self.view_count -= 1
        if self.view_count > 0:
            dynamo.update_item(
                TableName = 'Secrets',
                Key = { 'secret_id': { 'S': self.secret_id } },
                AttributeUpdates = { 'view_count': { 'N': str(self.view_count) } }
            )
        else:
            dynamo.delete_item(
                TableName = 'Secrets',
                Key = { 'secret_id': { 'S': self.secret_id } }
            )

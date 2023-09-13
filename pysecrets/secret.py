import json
import os
import time

from json.decoder import JSONDecodeError

import boto3
import botocore.exceptions

from .helpers import b64e, b64d, sanitize_view_count, tos
from .simple_crypt import SimpleCrypt


class Secret:
    def __init__(self, data=None, view_count=1, secret_id=None, file_name=None):
        self.data = data
        self.view_count = view_count
        self.secret_id = secret_id
        self.file_name = file_name
        self.dynamo = boto3.client('dynamodb', region_name='us-east-1')
        self.s3 = boto3.client('s3', region_name='us-east-1')

    def encrypt(self):
        sc = SimpleCrypt()
        sc.encrypt(self.data)
        self.crypt = sc
        return sc.secret_id, sc.password

    def decrypt(self):
        decrypted = self.crypt.decrypt()
        if decrypted is None:
            return None
        ret = decrypted if self.file_name else decrypted.decode('utf-8')
        return ret

    def store(self):
        ttl = int(time.time() + (86400 * int(os.environ.get('TTL_DAYS', 5))))
        item = {
            'secret_id': {'S': self.crypt.secret_id},
            'nonce': {'S': tos(b64e(self.crypt.nonce))},
            'salt': {'S': tos(b64e(self.crypt.salt))},
            'header': {'S': tos(b64e(self.crypt.header))},
            'ttl': {'N': str(ttl)},
            'view_count': {'N': str(self.view_count)},
        }
        if self.file_name is not None:
            self.__store_file()
            self.crypt.encrypt(json.dumps({'file_name': self.file_name}))
            data = tos(b64e(self.crypt.data))
        else:
            data = tos(b64e(self.crypt.data))
        item['data'] = {'S': data}
        self.dynamo.put_item(TableName='Secrets', Item=item)

    @classmethod
    def load(self, secret_id, passphrase):
        sec = Secret()
        resp = sec.dynamo.get_item(TableName='Secrets', Key={'secret_id': {'S': secret_id}})

        if resp.get('Item') is None:
            return None

        sec.secret_id = resp['Item']['secret_id']['S']
        sec.view_count = sanitize_view_count(resp['Item']['view_count']['N'])
        sec.crypt = SimpleCrypt(
            secret_id=resp['Item']['secret_id']['S'],
            password=passphrase,
            data=b64d(resp['Item']['data']['S']),
            nonce=b64d(resp['Item']['nonce']['S']),
            salt=b64d(resp['Item']['salt']['S']),
            header=b64d(resp['Item']['header']['S']),
        )
        sec.decrypted = sec.decrypt()
        if sec.decrypted is None:
            return None

        try:
            file_name = json.loads(sec.decrypted).get('file_name')
        except (JSONDecodeError, TypeError, AttributeError):
            return sec

        if file_name is not None:
            sec.file_name = file_name
            try:
                s3_resp = sec.s3.get_object(Bucket=os.environ.get('S3_BUCKET'), Key=resp['Item']['secret_id']['S'] + '.enc')
                sec.crypt.data = b64d(s3_resp['Body'].read())
            except botocore.exceptions.ClientError:
                return None
            sec.decrypted = sec.crypt.decrypt()

        return sec

    def __store_file(self):
        self.s3.put_object(
            Bucket=os.environ.get('S3_BUCKET'), ACL='private', Key=self.crypt.secret_id + '.enc', Body=b64e(self.crypt.data), ServerSideEncryption='aws:kms'
        )

    def burn(self):
        self.view_count -= 1
        if self.view_count > 0:
            self.dynamo.update_item(
                TableName='Secrets',
                Key={'secret_id': {'S': self.secret_id}},
                AttributeUpdates={'view_count': {'Value': {'N': str(self.view_count)}, 'Action': 'PUT'}},
            )
        else:
            if self.file_name is not None:
                self.s3.delete_object(Bucket=os.environ.get('S3_BUCKET'), Key=self.secret_id + '.enc')
            self.dynamo.delete_item(TableName='Secrets', Key={'secret_id': {'S': self.secret_id}})

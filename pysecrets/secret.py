import boto3
import json
import os
import time
from .simple_crypt import SimpleCrypt
from .helpers import b64s, b64e, b64d


class Secret:
    def __init__(self, data=None, view_count=1, secret_id=None, file_name=None):
        self.data = data
        self.view_count = view_count
        self.secret_id = secret_id
        self.file_name = file_name

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
        dynamo = boto3.client('dynamodb', region_name='us-east-1')
        item = {
            'secret_id': {'S': self.crypt.secret_id},
            'nonce': {'S': b64s(self.crypt.nonce)},
            'salt': {'S': b64s(self.crypt.salt)},
            'tag': {'S': b64s(self.crypt.tag)},
            'header': {'S': b64s(self.crypt.header)},
            'ttl': {'N': str(ttl)},
            'view_count': {'N': str(self.view_count)}
        }
        if self.file_name is not None:
            item['file_name'] = {'S': self.file_name}
            item['s3_info'] = {'S': json.dumps({
                'bucket': os.environ.get('S3_BUCKET'),
                'key': self.crypt.secret_id + '.enc'
            })}
            self.__store_file()
        else:
            item['data'] = {'S': b64s(self.crypt.data)}
        dynamo.put_item(TableName='Secrets', Item=item)

    @classmethod
    def load(self, secret_id):
        dynamo = boto3.client('dynamodb', region_name='us-east-1')
        try:
            resp = dynamo.get_item(
                TableName='Secrets',
                Key={'secret_id': {'S': secret_id}}
            )
        except dynamo.client.ResourceNotFoundException:
            return None
        if resp.get('Item') is None:
            return None
        if resp['Item'].get('file_name', None) is not None:
            s3 = boto3.client('s3', region_name='us-east-1')
            try:
                s3_resp = s3.get_object(Bucket=os.environ.get('S3_BUCKET'), Key=secret_id + '.enc')
                data = s3_resp['Body'].read().decode('utf-8')
            except s3.client.NoSuchKey:
                return None
            file_name = resp['Item']['file_name']['S']
        else:
            data = resp['Item']['data']['S']
            file_name = None
        sec = Secret(
            secret_id=resp['Item']['secret_id']['S'],
            view_count=int(resp['Item']['view_count']['N']),
            file_name=file_name
        )
        sec.crypt = SimpleCrypt(
            secret_id=resp['Item']['secret_id']['S'],
            data=b64d(data),
            nonce=b64d(resp['Item']['nonce']['S']),
            salt=b64d(resp['Item']['salt']['S']),
            tag=b64d(resp['Item']['tag']['S']),
            header=b64d(resp['Item']['header']['S'])
        )
        return sec

    def __store_file(self):
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(
            Bucket=os.environ.get('S3_BUCKET'),
            ACL='private',
            Key=self.crypt.secret_id + '.enc',
            Body=b64e(self.crypt.data),
            ServerSideEncryption='aws:kms'
        )

    def __burn(self):
        dynamo = boto3.client('dynamodb', region_name='us-east-1')
        s3 = boto3.client('s3', region_name='us-east-1')
        self.view_count -= 1
        if self.view_count > 0:
            dynamo.update_item(
                TableName='Secrets',
                Key={'secret_id': {'S': self.secret_id}},
                AttributeUpdates={'view_count': {'Value': {'N': str(self.view_count)}, 'Action': 'PUT'}}
            )
        else:
            if self.file_name is not None:
                s3.delete_object(Bucket=os.environ.get('S3_BUCKET'), Key=self.secret_id + '.enc')
            dynamo.delete_item(
                TableName='Secrets',
                Key={'secret_id': {'S': self.secret_id}}
            )

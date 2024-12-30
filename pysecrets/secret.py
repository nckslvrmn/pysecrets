import json
import time

from io import BytesIO
from json.decoder import JSONDecodeError

import boto3
import botocore.exceptions

from flask import current_app

from .helpers import b64e, b64d, sanitize_view_count
from .simple_crypt import SimpleCrypt


class Secret:
    def __init__(self, data=None, view_count=1, secret_id=None, file_name=None):
        self.data = data
        self.view_count = view_count
        self.secret_id = secret_id
        self.file_name = file_name
        self.dynamo = boto3.resource("dynamodb", region_name="us-east-1").Table(
            "Secrets"
        )
        self.s3 = boto3.resource("s3", region_name="us-east-1").Bucket(
            current_app.env["s3_bucket"]
        )

    def encrypt(self):
        sc = SimpleCrypt()
        sc.encrypt(self.data)
        self.crypt = sc
        return sc.secret_id, sc.passphrase

    def decrypt(self):
        decrypted = self.crypt.decrypt()
        if decrypted is None:
            return None
        ret = decrypted if self.file_name else decrypted.decode("utf-8")
        return ret

    def store(self):
        item = {
            "secret_id": self.crypt.secret_id,
            "nonce": b64e(self.crypt.nonce),
            "salt": b64e(self.crypt.salt),
            "header": b64e(self.crypt.header),
            "ttl": int(time.time() + (86400 * current_app.env["ttl_days"])),
            "view_count": self.view_count,
        }
        if self.file_name is not None:
            self.__store_file()
            self.crypt.encrypt(json.dumps({"file_name": self.file_name}))
            data = b64e(self.crypt.data)
        else:
            data = b64e(self.crypt.data)
        item["data"] = data
        self.dynamo.put_item(Item=item)

    @classmethod
    def load(self, secret_id, passphrase):
        sec = Secret()
        record = sec.dynamo.get_item(Key={"secret_id": secret_id}).get("Item")
        if record is None:
            return None

        sec.secret_id = record["secret_id"]
        sec.view_count = sanitize_view_count(record["view_count"])
        sec.crypt = SimpleCrypt(
            secret_id=record["secret_id"],
            passphrase=passphrase,
            data=b64d(record["data"]),
            nonce=b64d(record["nonce"]),
            salt=b64d(record["salt"]),
            header=b64d(record["header"]),
        )
        sec.decrypted = sec.decrypt()
        if sec.decrypted is None:
            return None

        try:
            file_name = json.loads(sec.decrypted).get("file_name")
        except (JSONDecodeError, TypeError, AttributeError):
            return sec

        if file_name is not None:
            sec.file_name = file_name
            try:
                bio = BytesIO()
                sec.s3.download_fileobj(record["secret_id"] + ".enc", bio)
                sec.crypt.data = b64d(bio.getvalue())
            except botocore.exceptions.ClientError:
                return None
            sec.decrypted = sec.crypt.decrypt()

        return sec

    def __store_file(self):
        self.s3.put_object(
            ACL="private",
            Key=self.crypt.secret_id + ".enc",
            Body=b64e(self.crypt.data, s=False),
            ServerSideEncryption="aws:kms",
        )

    def burn(self):
        self.view_count -= 1
        if self.view_count > 0:
            self.dynamo.update_item(
                Key={"secret_id": self.secret_id},
                AttributeUpdates={
                    "view_count": {
                        "Value": self.view_count,
                        "Action": "PUT",
                    }
                },
            )
        else:
            if self.file_name is not None:
                self.s3.delete_objects(
                    Delete={"Objects": [{"Key": self.secret_id + ".enc"}]}
                )
            self.dynamo.delete_item(Key={"secret_id": self.secret_id})

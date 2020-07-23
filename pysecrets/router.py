import json
import boto3
import base64
from .secret import Secret
from .helpers import sanitize_view_count

def encrypt(env):
    sec = Secret(env['body']['secret'], sanitize_view_count(env['body']['view_count']))
    secret_id, password = sec.encrypt()
    sec.store()
    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps({
            'secret_id': secret_id,
            'passphrase': password
        })
    }

def decrypt(env):
    sec = Secret.load(env['body']['secret_id'])
    if sec == None:
        return { 'statusCode': 404, 'body': '' }
    decrypted = sec.decrypt(env['body']['passphrase'])
    return {
        'statusCode': 200,
        'body': json.dumps({ 'data': decrypted })
    }

def router(env):
    if env['path'] == '/encrypt':
        return encrypt(env)
    elif env['path'] == '/decrypt':
        return decrypt(env)

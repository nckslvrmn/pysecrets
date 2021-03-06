import json
from .secret import Secret
from .helpers import sanitize_view_count, b64s


def encrypt(env):
    if env.get('params', None).get('file_name', None) is not None:
        sec = Secret(
            data=env['body'],
            file_name=env['params']['file_name']
        )
    else:
        sec = Secret(data=env['body']['secret'], view_count=sanitize_view_count(env['body']['view_count']))
    secret_id, password = sec.encrypt()
    sec.store()
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'secret_id': secret_id,
            'passphrase': password
        })
    }


def decrypt(env):
    sec = Secret.load(env['body']['secret_id'])
    if sec is None:
        return {'statusCode': 404, 'body': ''}
    decrypted = sec.decrypt(env['body']['passphrase'])
    if sec.file_name is not None:
        body = {'data': b64s(decrypted), 'file_name': sec.file_name}
    else:
        body = {'data': decrypted}
    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }


def router(env):
    if env['path'] == '/encrypt':
        return encrypt(env)
    elif env['path'] == '/decrypt':
        return decrypt(env)

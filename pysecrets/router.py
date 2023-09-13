import json

from .helpers import sanitize_view_count, b64e, tos
from .secret import Secret


def encrypt(env):
    if env.get('params').get('file_name') is not None:
        body = env['body'].encode() if isinstance(env['body'], str) else env['body']
        if type(body) is dict:
            body = json.dumps(body).encode()
        sec = Secret(data=b64e(body), file_name=env['params']['file_name'])
    else:
        sec = Secret(data=env['body']['secret'], view_count=sanitize_view_count(env['body']['view_count']))
    secret_id, password = sec.encrypt()
    sec.store()
    return {'statusCode': 200, 'body': json.dumps({'secret_id': secret_id, 'passphrase': password})}


def decrypt(env):
    sec = Secret.load(env['body']['secret_id'], env['body']['passphrase'])
    print(f"AUDIT: attempting to decrypt {env['body']['secret_id']} from {env['ip']}")

    if sec is None:
        return {'statusCode': 404, 'body': ''}

    sec.burn()

    if sec.file_name is not None:
        body = {'data': tos(sec.decrypted), 'file_name': sec.file_name}
    else:
        body = {'data': sec.decrypted}

    print(f"AUDIT: success decrypting {sec.secret_id} from {env['ip']}, {sec.view_count} views remaining")
    return {'statusCode': 200, 'body': json.dumps(body)}


def router(env):
    match env['path']:
        case '/encrypt':
            return encrypt(env)
        case '/decrypt':
            return decrypt(env)
        case _:
            return {'statusCode': 404, 'body': ''}

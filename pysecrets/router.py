import json

from .helpers import sanitize_view_count, b64e, tos
from .secret import Secret


def encrypt(env):
    if env.get('params').get('file_name') is not None:
        sec = Secret(
            data=env['body'],
            file_name=env['params']['file_name']
        )
        if type(sec.data) is dict:
            sec.data = json.dumps(sec.data).encode()
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
    sec = Secret.load(env['body']['secret_id'], env['body']['passphrase'])
    if sec is None:
        return {'statusCode': 404, 'body': ''}

    sec.burn()

    if sec.file_name is not None:
        body = {'data': tos(b64e(sec.decrypted)), 'file_name': sec.file_name}
    else:
        body = {'data': sec.decrypted}

    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }


def serve_static(asset):
    with open(f"static/{asset['path']}") as file:
        static = file.read()

    return {
        'statusCode': 200,
        'headers': {'Content-Type': asset['type']},
        'body': static
    }


def router(env):
    static_assets = {
      '/': {
        'path': 'index.html',
        'type': 'text/html'
      },
      '/files': {
        'path': 'files.html',
        'type': 'text/html'
      },
      '/site.css': {
        'path': 'site.css',
        'type': 'text/css'
      },
      '/main.js': {
        'path': 'main.js',
        'type': 'text/javascript'
      }
    }

    if env['path'] in static_assets.keys():
        return serve_static(static_assets[env['path']])
    elif env['path'].startswith('/secret/'):
        return serve_static({'path': 'secret.html', 'type': 'text/html'})
    elif env['path'] == '/encrypt':
        return encrypt(env)
    elif env['path'] == '/decrypt':
        return decrypt(env)

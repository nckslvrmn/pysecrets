import json
import os

from jinja2 import Template

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


def render_html(env, template_name):
    secret_id = None
    if env['path'].startswith('/secret/'):
        secret_id = env['path'].split('/')[-1]

    with open(f'templates/{template_name}.html.j2') as file:
        template = Template(file.read())

    rendered = template.render(
        base_domain=os.environ.get('BASE_DOMAIN'),
        secret_id=secret_id
    )
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': rendered
    }


def router(env):
    if env['path'] == '/':
        return render_html(env, 'index')
    elif env['path'] == '/files':
        return render_html(env, 'files')
    elif env['path'].startswith('/secret/'):
        return render_html(env, 'secret')
    elif env['path'] == '/encrypt':
        return encrypt(env)
    elif env['path'] == '/decrypt':
        return decrypt(env)

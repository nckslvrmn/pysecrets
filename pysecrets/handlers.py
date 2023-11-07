import io

from flask import request, Response, send_file
from .helpers import sanitize_view_count, log_line
from .secret import Secret


def encrypt():
    if len(request.files) > 0:
        sec = Secret(data=request.files['file'].read(), file_name=request.files['file'].filename)
    else:
        data = request.json
        sec = Secret(data=data['secret'], view_count=sanitize_view_count(data['view_count']))
    secret_id, passphrase = sec.encrypt()
    sec.store()
    return {'secret_id': secret_id, 'passphrase': passphrase}


def decrypt():
    data = request.json
    sec = Secret.load(data['secret_id'], data['passphrase'])
    log_line(f"{request.headers.get('X-Forwarded-For')} AUDIT: attempting to decrypt {data['secret_id']}")

    if sec is None:
        log_line(f"{request.headers.get('X-Forwarded-For')} AUDIT: decrypt failed for {data['secret_id']}")
        return Response('', status=404)

    sec.burn()

    log_line(f"{request.headers.get('X-Forwarded-For')} AUDIT: decrypt success {sec.secret_id}, {sec.view_count} views remaining")
    if sec.file_name is not None:
        return send_file(io.BytesIO(sec.decrypted), as_attachment=True, download_name=sec.file_name)

    return {'data': sec.decrypted}

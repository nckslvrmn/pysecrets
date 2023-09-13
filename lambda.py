import json

from pysecrets.router import router
from pysecrets.helpers import b64d


def handler(event, context):
    raw_body = b64d(event['body']) if event['isBase64Encoded'] else event['body']
    try:
        body = json.loads(raw_body)
    except (ValueError, TypeError):
        body = raw_body

    env = {
        'method': event['requestContext']['httpMethod'],
        'path': event['requestContext']['path'],
        'params': event['queryStringParameters'] or {},
        'body': body,
        'ip': event.get('headers', {}).get('x-forwarded-for', 'UNKOWN IP'),
    }

    resp = router(env)
    resp['isBase64Encoded'] = False
    resp['headers'] = resp.get('headers', {'Content-Type': 'application/json'})
    return resp

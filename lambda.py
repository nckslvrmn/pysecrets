from base64 import b64decode as b64d
import json
from pysecrets.router import router

def handler(event, context):
    raw_body = b64d(event['body']) if event['isBase64Encoded'] else event['body']
    try:
        body = json.loads(raw_body)
    except ValueError:
        body = raw_body

    env = {
        'method': event['requestContext']['httpMethod'],
        'path': event['requestContext']['path'],
        'params': event['queryStringParameters'] if event['queryStringParameters'] != None else '',
        'body': body
    }

    resp = router(env)
    resp['isBase64Encoded'] = False
    resp['headers'] = resp.get('headers', { 'Content-Type': 'application/json' })
    return resp

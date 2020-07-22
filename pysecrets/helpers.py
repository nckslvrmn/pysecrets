from Cryptodome.Random import get_random_bytes
from Cryptodome.Random.random import choice
import base64
import string

def rand_string(c, url_safe=True):
    accepted_chars = string.ascii_letters + string.digits
    if not url_safe:
        accepted_chars += '!#$%&*+-=?@_~'
    return ''.join(choice(accepted_chars) for _ in range(c))

def b64s(b, url_safe=False):
    command = base64.urlsafe_b64encode if url_safe else base64.b64encode
    return command(b).decode('utf-8')

def b64d(s, url_safe=False):
    command = base64.urlsafe_b64decode if url_safe else base64.b64decode
    return command(s)

def sanitize_view_count(view_count):
    vc = abs(int(view_count))
    if vc == None or vc == 0:
        return 1
    elif vc > 10:
        return 10
    else:
        return vc

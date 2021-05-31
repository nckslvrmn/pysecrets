import base64
import secrets
import string


def rand_string(c, url_safe=True):
    accepted_chars = string.ascii_letters + string.digits
    if not url_safe:
        accepted_chars += '!#$%&*+-=?@_~'
    return ''.join(secrets.choice(accepted_chars) for _ in range(c))


def b64e(b, url_safe=False):
    command = base64.urlsafe_b64encode if url_safe else base64.b64encode
    return command(b)


def b64d(s, url_safe=False):
    command = base64.urlsafe_b64decode if url_safe else base64.b64decode
    return command(s)


def tos(b):
    return b.decode('utf-8')


def sanitize_view_count(view_count):
    vc = abs(int(view_count))
    if vc is None or vc == 0:
        return 1
    elif vc > 10:
        return 10
    else:
        return vc

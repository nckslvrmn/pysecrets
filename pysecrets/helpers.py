import base64
import logging
import os
import secrets
import string

from datetime import datetime, timezone

from flask import current_app


def load_env():
    current_app.env = {
        "s3_bucket": os.environ.get("S3_BUCKET"),
        "ttl_days": int(os.environ.get("TTL_DAYS", 7)),
    }


def rand_string(c, url_safe=True):
    accepted_chars = string.ascii_letters + string.digits
    if not url_safe:
        accepted_chars += "!#$%&*+-=?@_~"
    return "".join(secrets.choice(accepted_chars) for _ in range(c))


def b64e(b, url_safe=False, s=True):
    command = base64.urlsafe_b64encode if url_safe else base64.b64encode
    return command(b).decode("utf-8") if s else command(b)


def b64d(s, url_safe=False):
    command = base64.urlsafe_b64decode if url_safe else base64.b64decode
    return command(s)


def sanitize_view_count(view_count):
    vc = abs(int(view_count))
    if vc is None or vc == 0:
        return 1
    elif vc > 10:
        return 10
    else:
        return vc


def log_line(message):
    log = logging.getLogger("gunicorn.access")
    now = datetime.now(timezone.utc)
    formatted = now.strftime("%d/%b/%Y:%H:%M:%S %z")
    log.info(f"[{formatted}] {message}")

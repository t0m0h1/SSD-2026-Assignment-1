from functools import wraps
from flask_login import current_user
from flask import abort
from models import log_action


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Not logged in
            if not current_user.is_authenticated:
                return abort(403)

            # Wrong role
            if current_user.role not in roles:
                log_action(current_user.username, "Unauthorized access attempt")
                return abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator
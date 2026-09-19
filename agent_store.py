"""Process-local approval requests and confirmed demo results."""

from secrets import token_urlsafe
from threading import Lock
from time import monotonic

PENDING_TTL_SECONDS = 600
_lock = Lock()
_pending = {}
_recorded = {}


def prepare_result(application_id, result):
    with _lock:
        now = monotonic()
        for token, request in list(_pending.items()):
            if request["expires_at"] <= now:
                del _pending[token]
        if application_id in _recorded or any(
            request["application_id"] == application_id for request in _pending.values()
        ):
            return None
        token = token_urlsafe(32)
        _pending[token] = {
            "application_id": application_id,
            "result": result,
            "expires_at": now + PENDING_TTL_SECONDS,
        }
        return token


def confirm_result(token):
    with _lock:
        request = _pending.pop(token, None)
        if request is None or request["expires_at"] <= monotonic():
            return None
        result = {
            "application_id": request["application_id"],
            "result": request["result"],
        }
        _recorded[request["application_id"]] = result
        return result

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from .config import settings


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str, salt: str | None = None) -> str:
    local_salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256(f"{local_salt}:{password}".encode()).hexdigest()
    return f"{local_salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def create_token(user_id: int, username: str) -> str:
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=settings.token_exp_minutes)).timestamp())
    payload = {"sub": user_id, "username": username, "exp": exp}
    payload_raw = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(settings.secret_key.encode(), payload_raw.encode(), hashlib.sha256).digest()
    return f"{payload_raw}.{_b64(sig)}"


def decode_token(token: str) -> dict:
    try:
        payload_raw, sig_raw = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format") from exc
    expected = _b64(hmac.new(settings.secret_key.encode(), payload_raw.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, sig_raw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    payload = json.loads(_unb64(payload_raw).decode())
    if payload.get("exp", 0) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return payload

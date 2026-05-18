from fastapi import Header, HTTPException, status

from .auth import decode_token


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    payload = decode_token(authorization.split(" ", 1)[1])
    return {"id": int(payload["sub"]), "username": payload["username"]}

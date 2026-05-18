from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/gif"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}


def validate_upload(file: UploadFile, size_bytes: int) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if file.content_type not in ALLOWED_TYPES or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")
    if size_bytes > settings.max_upload_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum allowed size")


def save_upload(file_name: str, content: bytes) -> Path:
    extension = Path(file_name).suffix.lower()
    target = settings.upload_dir / f"{uuid4().hex}{extension}"
    target.write_bytes(content)
    return target

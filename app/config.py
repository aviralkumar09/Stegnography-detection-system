import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "Steganography Detection System")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    token_exp_minutes: int = int(os.getenv("TOKEN_EXP_MINUTES", "120"))
    db_path: Path = Path(os.getenv("DB_PATH", "steg_detection.db"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    report_dir: Path = Path(os.getenv("REPORT_DIR", "reports"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))


settings = Settings()

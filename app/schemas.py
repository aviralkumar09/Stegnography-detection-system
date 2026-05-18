from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=200)


class AuthResponse(BaseModel):
    token: str
    username: str


class UploadResponse(BaseModel):
    upload_id: int
    file_name: str
    mime_type: str
    size_bytes: int
    status: str


class DetectionRequest(BaseModel):
    notify_on_suspicious: bool = True


class ReportSummary(BaseModel):
    report_id: int
    upload_id: int
    risk_score: float
    risk_level: str
    classification: str
    summary: str


class NotificationItem(BaseModel):
    id: int
    message: str
    severity: str
    is_read: bool
    created_at: str

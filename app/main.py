import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .auth import create_token, hash_password, verify_password
from .config import settings
from .database import get_conn, init_db, utc_now
from .dependencies import get_current_user
from .detection.decision import evaluate_decision
from .detection.engine import run_detection_pipeline
from .schemas import AuthRequest, AuthResponse, DetectionRequest, NotificationItem, ReportSummary, UploadResponse
from .services.notifications import create_notification
from .services.storage import save_upload, validate_upload

app = FastAPI(title="Steganography Detection System API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.post("/api/auth/register", response_model=AuthResponse)
def register(payload: AuthRequest):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM users WHERE username = ?", (payload.username,)).fetchone():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (payload.username, hash_password(payload.password), utc_now()),
        )
        user = conn.execute("SELECT id, username FROM users WHERE username = ?", (payload.username,)).fetchone()
    return AuthResponse(token=create_token(user["id"], user["username"]), username=user["username"])


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: AuthRequest):
    with get_conn() as conn:
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (payload.username,)
        ).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return AuthResponse(token=create_token(user["id"], user["username"]), username=user["username"])


@app.post("/api/files/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    content = await file.read()
    validate_upload(file, len(content))
    stored_path = save_upload(file.filename or "upload.bin", content)
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO uploads (user_id, original_name, stored_path, mime_type, size_bytes, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user["id"], file.filename, str(stored_path), file.content_type, len(content), "uploaded", utc_now()),
        )
    return UploadResponse(
        upload_id=cur.lastrowid,
        file_name=file.filename or "",
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        status="uploaded",
    )


@app.post("/api/detection/{upload_id}/run", response_model=ReportSummary)
def run_detection(upload_id: int, payload: DetectionRequest, user: dict = Depends(get_current_user)):
    with get_conn() as conn:
        upload = conn.execute("SELECT * FROM uploads WHERE id = ? AND user_id = ?", (upload_id, user["id"])).fetchone()
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    pipeline = run_detection_pipeline(Path(upload["stored_path"]))
    decision = evaluate_decision(pipeline["results"])
    with get_conn() as conn:
        conn.execute("UPDATE uploads SET status = ? WHERE id = ?", ("processed", upload_id))
        for item in pipeline["results"]:
            conn.execute(
                """
                INSERT INTO analysis_results (upload_id, module_name, score, details_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (upload_id, item["module"], item["score"], json.dumps(item["details"]), utc_now()),
            )
        cur = conn.execute(
            """
            INSERT INTO reports (upload_id, user_id, risk_score, risk_level, classification, summary, evidence_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                upload_id,
                user["id"],
                decision["risk_score"],
                decision["risk_level"],
                decision["classification"],
                decision["summary"],
                json.dumps({"preprocessing": pipeline["preprocessing"], "results": pipeline["results"]}),
                utc_now(),
            ),
        )
    report_id = cur.lastrowid
    if payload.notify_on_suspicious and decision["classification"] == "suspicious":
        create_notification(user["id"], report_id, "Suspicious file detected and report generated.", "high")
    return ReportSummary(report_id=report_id, upload_id=upload_id, **decision)


@app.get("/api/reports/{report_id}")
def get_report(report_id: int, user: dict = Depends(get_current_user)):
    with get_conn() as conn:
        report = conn.execute("SELECT * FROM reports WHERE id = ? AND user_id = ?", (report_id, user["id"])).fetchone()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return {
        "report_id": report["id"],
        "upload_id": report["upload_id"],
        "risk_score": report["risk_score"],
        "risk_level": report["risk_level"],
        "classification": report["classification"],
        "summary": report["summary"],
        "evidence": json.loads(report["evidence_json"]),
        "created_at": report["created_at"],
    }


@app.get("/api/reports")
def list_reports(user: dict = Depends(get_current_user)):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, upload_id, risk_score, risk_level, classification, summary, created_at FROM reports WHERE user_id = ? ORDER BY id DESC",
            (user["id"],),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/reports/{report_id}/download")
def download_report(report_id: int, user: dict = Depends(get_current_user)):
    report = get_report(report_id, user)
    path = settings.report_dir / f"report_{report_id}.json"
    path = path.resolve()
    if path.parent != settings.report_dir.resolve():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report path")
    if not path.exists():
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return FileResponse(path)


@app.get("/api/notifications", response_model=list[NotificationItem])
def list_notifications(user: dict = Depends(get_current_user)):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, message, severity, is_read, created_at FROM notifications WHERE user_id = ? ORDER BY id DESC",
            (user["id"],),
        ).fetchall()
    return [
        NotificationItem(
            id=row["id"],
            message=row["message"],
            severity=row["severity"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

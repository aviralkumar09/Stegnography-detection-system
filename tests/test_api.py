from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.main import app

client = TestClient(app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_auth_upload_detect_report_flow(tmp_path):
    config.settings.db_path = tmp_path / "test.db"
    config.settings.upload_dir = tmp_path / "uploads"
    config.settings.report_dir = tmp_path / "reports"
    from app.database import init_db

    init_db()
    reg = client.post("/api/auth/register", json={"username": "tester1", "password": "Str0ngPass!2026"})
    assert reg.status_code == 200
    token = reg.json()["token"]
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (32, 32), color=(10, 20, 30)).save(image_path)
    files = {"file": ("sample.png", image_path.read_bytes(), "image/png")}
    up = client.post("/api/files/upload", headers=auth_headers(token), files=files)
    assert up.status_code == 200
    upload_id = up.json()["upload_id"]
    run = client.post(f"/api/detection/{upload_id}/run", headers=auth_headers(token), json={"notify_on_suspicious": True})
    assert run.status_code == 200
    report_id = run.json()["report_id"]
    report = client.get(f"/api/reports/{report_id}", headers=auth_headers(token))
    assert report.status_code == 200
    assert report.json()["classification"] in {"benign", "suspicious"}
    notifications = client.get("/api/notifications", headers=auth_headers(token))
    assert notifications.status_code == 200

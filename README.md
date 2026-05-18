# Steganography Detection System

Full-stack steganography detection workflow with authentication, upload validation, modular analysis pipeline, decision fusion, report generation, storage, and notifications.

## Project Structure

- `app/main.py` - FastAPI backend endpoints
- `app/auth.py` - registration/login authentication
- `app/database.py` - SQLite persistence
- `app/services/` - upload validation/storage + notification service
- `app/detection/` - pre-processing, statistical, RS, histogram, texture, transform, AI, anomaly, and decision modules
- `frontend/index.html` - login/registration + dashboard UI
- `tests/` - API flow and detection module tests

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Data Flow

1. User registers/logs in.
2. User uploads file; system validates format/size and stores metadata.
3. Detection engine runs pre-processing and all analysis modules.
4. Decision engine fuses outputs into risk score/classification.
5. Report is stored and retrievable.
6. Suspicious detections generate notifications.
7. Dashboard shows final outcome and evidence.

from app.database import get_conn, utc_now


def create_notification(user_id: int, report_id: int | None, message: str, severity: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO notifications (user_id, report_id, message, severity, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (user_id, report_id, message, severity, utc_now()),
        )

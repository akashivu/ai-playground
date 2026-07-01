import sqlite3
from datetime import datetime
from utils.logger import logger


class UsageTrackingService:
    """Logs request metadata to SQLite for analytics."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self.db_path = db_path

    def log_request(
        self,
        user_id: str,
        session_id: str,
        intent: str,
        latency: float,
    ) -> None:
        """Persists a single request log entry."""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO usage_logs (
                        user_id,
                        session_id,
                        intent,
                        latency,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        session_id,
                        intent,
                        round(latency, 4),
                        datetime.now().isoformat(),
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to log usage: {e}")


usage_tracking_service = UsageTrackingService()

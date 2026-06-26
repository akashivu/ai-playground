import os
import sqlite3
from datetime import datetime, UTC, timedelta

DEFAULT_LIMIT = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
DEFAULT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "1"))


class RateLimitService:
    """SQLite-backed rate limiter scoped by authenticated user."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def allow_request(
        self,
        user_id: str,
        session_id: str,
        limit: int = DEFAULT_LIMIT,
        window_minutes: int = DEFAULT_WINDOW,
    ) -> bool:
        """
        Returns True if the authenticated user is allowed to make another request.
        Cleans up expired records before counting to keep the table lean.
        """
        now = datetime.now(UTC)
        cutoff = (now - timedelta(minutes=window_minutes)).isoformat()

        with self._connect() as conn:
            conn.execute(
                "DELETE FROM rate_limits WHERE created_at < ?",
                (cutoff,),
            )

            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM rate_limits
                WHERE user_id = ?
                AND created_at >= ?
                """,
                (user_id, cutoff),
            ).fetchone()[0]

            if count >= limit:
                return False

            conn.execute(
                """
                INSERT INTO rate_limits (user_id, session_id, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, session_id, now.isoformat()),
            )

        return True


rate_limit_service = RateLimitService()
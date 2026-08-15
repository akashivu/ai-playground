import json
import sqlite3
import os
from datetime import datetime, UTC


class PersistentConversationStore:
    """SQLite-backed conversation store with booking, recommendation, and itinerary session support."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()

    def _init_db(self) -> None:
        """Creates all tables and indexes if they don't exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    user_id     TEXT NOT NULL,
                    session_id  TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    PRIMARY KEY (user_id, session_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role       TEXT NOT NULL,
                    content    TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id, session_id)
                        REFERENCES sessions (user_id, session_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user_session
                    ON messages (user_id, session_id)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS booking_sessions (
                    user_id      TEXT NOT NULL,
                    session_id   TEXT NOT NULL,
                    booking_data TEXT NOT NULL,
                    updated_at   TEXT NOT NULL,
                    PRIMARY KEY (user_id, session_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_booking_sessions
                    ON booking_sessions (user_id, session_id)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendation_sessions (
                    user_id             TEXT NOT NULL,
                    session_id          TEXT NOT NULL,
                    recommendation_data TEXT NOT NULL,
                    updated_at          TEXT NOT NULL,
                    PRIMARY KEY (user_id, session_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recommendation_sessions
                    ON recommendation_sessions (user_id, session_id)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itinerary_sessions (
                    user_id        TEXT NOT NULL,
                    session_id     TEXT NOT NULL,
                    itinerary_data TEXT NOT NULL,
                    updated_at     TEXT NOT NULL,
                    PRIMARY KEY (user_id, session_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_itinerary_sessions
                    ON itinerary_sessions (user_id, session_id)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    intent     TEXT NOT NULL,
                    latency    REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_logs
                    ON usage_logs (user_id, created_at)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage_logs (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id           TEXT NOT NULL,
                    session_id        TEXT NOT NULL,
                    intent            TEXT NOT NULL,
                    model             TEXT NOT NULL,
                    prompt_tokens     INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens      INTEGER NOT NULL,
                    estimated_cost    REAL NOT NULL,
                    created_at        TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_token_logs
                    ON token_usage_logs (user_id, created_at)
            """)

    # --- session / message methods ---

    def session_exists(self, user_id: str, session_id: str) -> bool:
        """Returns True if the session exists and belongs to this user."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            ).fetchone()
        return row is not None

    def add_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """Appends a message and creates the session row if needed."""
        now = self._now()
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO sessions (user_id, session_id, created_at, last_active)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, session_id) DO UPDATE SET last_active = ?
            """, (user_id, session_id, now, now, now))
            conn.execute("""
                INSERT INTO messages (user_id, session_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, role, content, now))

    def get_messages(self, user_id: str, session_id: str, max_messages: int = 10) -> list[dict]:
        """Returns last N messages for context window."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT role, content FROM messages
                WHERE user_id = ? AND session_id = ?
                ORDER BY id DESC LIMIT ?
            """, (user_id, session_id, max_messages)).fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_session(self, user_id: str, session_id: str) -> list[dict]:
        """Returns full conversation history."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT role, content FROM messages
                WHERE user_id = ? AND session_id = ?
                ORDER BY id ASC
            """, (user_id, session_id)).fetchall()
        return [dict(row) for row in rows]

    def clear_session(self, user_id: str, session_id: str) -> None:
        """Deletes the session and all its messages."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM messages WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )

    # --- booking session methods ---

    def save_booking(self, user_id: str, session_id: str, booking_data: dict) -> None:
        """Persists booking details for a user's session."""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO booking_sessions (user_id, session_id, booking_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, session_id) DO UPDATE SET
                    booking_data = excluded.booking_data,
                    updated_at   = excluded.updated_at
            """, (user_id, session_id, json.dumps(booking_data), self._now()))

    def get_booking(self, user_id: str, session_id: str) -> dict:
        """Returns persisted booking details for a user's session."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT booking_data FROM booking_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            ).fetchone()
        return json.loads(row["booking_data"]) if row else {}

    def clear_booking(self, user_id: str, session_id: str) -> None:
        """Removes booking session data."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM booking_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )

    # --- recommendation session methods ---

    def save_recommendation(self, user_id: str, session_id: str, recommendation_data: dict) -> None:
        """Persists recommendation details for a user's session."""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO recommendation_sessions (user_id, session_id, recommendation_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, session_id) DO UPDATE SET
                    recommendation_data = excluded.recommendation_data,
                    updated_at          = excluded.updated_at
            """, (user_id, session_id, json.dumps(recommendation_data), self._now()))

    def get_recommendation(self, user_id: str, session_id: str) -> dict:
        """Returns persisted recommendation details for a user's session."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT recommendation_data FROM recommendation_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            ).fetchone()
        return json.loads(row["recommendation_data"]) if row else {}

    def clear_recommendation(self, user_id: str, session_id: str) -> None:
        """Removes recommendation session data."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM recommendation_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )

    # --- itinerary session methods ---

    def save_itinerary(self, user_id: str, session_id: str, itinerary_data: dict) -> None:
        """Persists itinerary details for a user's session."""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO itinerary_sessions (user_id, session_id, itinerary_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, session_id) DO UPDATE SET
                    itinerary_data = excluded.itinerary_data,
                    updated_at     = excluded.updated_at
            """, (user_id, session_id, json.dumps(itinerary_data), self._now()))

    def get_itinerary(self, user_id: str, session_id: str) -> dict:
        """Returns persisted itinerary details for a user's session."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT itinerary_data FROM itinerary_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            ).fetchone()
        return json.loads(row["itinerary_data"]) if row else {}

    def clear_itinerary(self, user_id: str, session_id: str) -> None:
        """Removes itinerary session data."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM itinerary_sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )

    def get_user_sessions(self, user_id: str) -> list[dict]:
        """Returns all sessions for a user, most recently active first."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT session_id, created_at, last_active
                FROM sessions
                WHERE user_id = ?
                ORDER BY last_active DESC
            """, (user_id,)).fetchall()
        return [dict(row) for row in rows]

    def delete_session(self, user_id: str, session_id: str) -> None:
        """Deletes a conversation and all its messages."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM messages WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ? AND session_id = ?",
                (user_id, session_id)
            )

    def touch_session(self, user_id: str, session_id: str) -> None:
        """Updates the last activity timestamp for a session."""
        with self._connect() as conn:
            conn.execute("""
                UPDATE sessions SET last_active = ?
                WHERE user_id = ? AND session_id = ?
            """, (self._now(), user_id, session_id))
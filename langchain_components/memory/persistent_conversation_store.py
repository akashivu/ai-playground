import sqlite3
import os
from datetime import datetime


class PersistentConversationStore:
    """SQLite-backed conversation store. Drop-in replacement for ConversationStore."""

    def __init__(self, db_path: str = "data/conversations.db") -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Creates tables if they don't exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

    def session_exists(self, session_id: str) -> bool:
        """Returns True if session exists in database."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
        return row is not None

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Appends a message and creates session if needed."""
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, created_at, last_active)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET last_active = ?
            """, (session_id, now, now, now))
            conn.execute("""
                INSERT INTO messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, content, now))

    def get_messages(self, session_id: str, max_messages: int = 10) -> list[dict]:
        """Returns last N messages for context window."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT role, content FROM messages
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?
            """, (session_id, max_messages)).fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def get_session(self, session_id: str) -> list[dict]:
        """Returns full conversation history."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT role, content FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
            """, (session_id,)).fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]

    def clear_session(self, session_id: str) -> None:
        """Deletes session and all its messages."""
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
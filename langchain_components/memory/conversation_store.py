from collections import defaultdict
from datetime import datetime, timedelta


class ConversationStore:
    """In-memory conversation history store with TTL expiry."""

    def __init__(self, ttl_minutes: int = 60) -> None:
        self.sessions: dict[str, list[dict]] = defaultdict(list)
        self._last_active: dict[str, datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def _is_expired(self, session_id: str) -> bool:
        last = self._last_active.get(session_id)
        if last is None:
            return False
        return datetime.now() - last > self._ttl

    def session_exists(self, session_id: str) -> bool:
        """Returns True if session exists and has not expired."""
        if self._is_expired(session_id):
            self.clear_session(session_id)
            return False
        return session_id in self.sessions

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Appends a message to the session history."""
        if self._is_expired(session_id):
            self.clear_session(session_id)
        self.sessions[session_id].append({"role": role, "content": content})
        self._last_active[session_id] = datetime.now()

    def get_messages(self, session_id: str, max_messages: int = 10) -> list[dict]:
        """Returns last N messages for a session."""
        if self._is_expired(session_id):
            self.clear_session(session_id)
            return []
        return self.sessions.get(session_id, [])[-max_messages:]

    def get_session(self, session_id: str) -> list[dict]:
        """Returns full conversation history for a session."""
        if self._is_expired(session_id):
            self.clear_session(session_id)
            return []
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """Removes all history for a session."""
        self.sessions.pop(session_id, None)
        self._last_active.pop(session_id, None)
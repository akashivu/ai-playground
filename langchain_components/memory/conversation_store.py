from collections import defaultdict
from datetime import datetime, timedelta


class ConversationStore:
    """In-memory conversation history store with TTL expiry, scoped by user and session."""

    def __init__(self, ttl_minutes: int = 60) -> None:
        # Structure: { user_id: { session_id: [messages] } }
        self.sessions: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
        self._last_active: dict[tuple[str, str], datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def _key(self, user_id: str, session_id: str) -> tuple[str, str]:
        return (user_id, session_id)

    def _is_expired(self, user_id: str, session_id: str) -> bool:
        last = self._last_active.get(self._key(user_id, session_id))
        if last is None:
            return False
        return datetime.now() - last > self._ttl

    def session_exists(self, user_id: str, session_id: str) -> bool:
        if self._is_expired(user_id, session_id):
            self.clear_session(user_id, session_id)
            return False
        return session_id in self.sessions.get(user_id, {})

    def add_message(self, user_id: str, session_id: str, role: str, content: str) -> None:
        if self._is_expired(user_id, session_id):
            self.clear_session(user_id, session_id)
        self.sessions[user_id][session_id].append({"role": role, "content": content})
        self._last_active[self._key(user_id, session_id)] = datetime.now()

    def get_messages(self, user_id: str, session_id: str, max_messages: int = 10) -> list[dict]:
        if self._is_expired(user_id, session_id):
            self.clear_session(user_id, session_id)
            return []
        return self.sessions.get(user_id, {}).get(session_id, [])[-max_messages:]

    def get_session(self, user_id: str, session_id: str) -> list[dict]:
        if self._is_expired(user_id, session_id):
            self.clear_session(user_id, session_id)
            return []
        return self.sessions.get(user_id, {}).get(session_id, [])

    def get_user_sessions(self, user_id: str) -> list[str]:
        """Returns all active session IDs for a user."""
        return list(self.sessions.get(user_id, {}).keys())

    def clear_session(self, user_id: str, session_id: str) -> None:
        if user_id in self.sessions:
            self.sessions[user_id].pop(session_id, None)
            if not self.sessions[user_id]:
                del self.sessions[user_id]
        self._last_active.pop(self._key(user_id, session_id), None)
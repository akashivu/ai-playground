from langchain_components.memory.exceptions import MemoryStorageError
from langchain_components.memory.runtime.models import SessionMemory


class SessionMemoryStore:
    def __init__(self):
        self._sessions: dict[str, SessionMemory] = {}

    def load(self, session_id: str) -> SessionMemory:
        return self._sessions.get(session_id, SessionMemory(session_id=session_id))

    def save(self, session: SessionMemory) -> None:
        if not session.session_id:
            raise MemoryStorageError("session_memory","session_id is required",)
        self._sessions[session.session_id] = session

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
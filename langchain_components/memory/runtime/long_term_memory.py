import json
import sqlite3

from langchain_components.memory.exceptions import MemoryLoadError, MemorySaveError
from langchain_components.memory.runtime.models import LongTermMemory


class LongTermMemoryStore:
    def __init__(self, db_path: str = "runtime_memory.db"):
        self._db_path = db_path
        self._init_table()

    def _connect(self):
        return sqlite3.connect(self._db_path)

    def _init_table(self):
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS long_term_memory ("
                "user_id TEXT PRIMARY KEY, variables TEXT NOT NULL)"
            )

    def load(self, user_id: str) -> LongTermMemory:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT variables FROM long_term_memory WHERE user_id = ?", (user_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise MemoryLoadError(str(exc)) from exc

        variables = json.loads(row[0]) if row else {}
        return LongTermMemory(user_id=user_id, variables=variables)

    def save(self, memory: LongTermMemory) -> None:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO long_term_memory (user_id, variables) VALUES (?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET variables = excluded.variables",
                    (memory.user_id, json.dumps(memory.variables)),
                )
        except sqlite3.Error as exc:
            raise MemorySaveError(str(exc)) from exc

    def clear(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM long_term_memory WHERE user_id = ?", (user_id,))
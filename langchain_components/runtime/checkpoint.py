from __future__ import annotations

import logging
import sqlite3
import time
import uuid
from typing import TYPE_CHECKING, Protocol

from pydantic import ValidationError

from langchain_components.runtime.checkpoint_models import (
    CHECKPOINT_SCHEMA_VERSION,
    ExecutionCheckpoint,
    ExecutionStatus,
    RuntimeStepSnapshot,
)
from langchain_components.runtime.exceptions import (
    CheckpointAgentMismatchError,
    CheckpointCorruptError,
    CheckpointIdentityMismatchError,
    CheckpointNotFoundError,
    CheckpointVersionError,
)

if TYPE_CHECKING:
    from langchain_components.runtime.context import RuntimeContext

logger = logging.getLogger(__name__)


class CheckpointStore(Protocol):
    def save(self, checkpoint: ExecutionCheckpoint) -> None: ...
    def load(self, execution_id: str) -> ExecutionCheckpoint | None: ...
    def exists(self, execution_id: str) -> bool: ...
    def delete(self, execution_id: str) -> None: ...


class InMemoryCheckpointStore:
   

    def __init__(self):
        self._checkpoints: dict[str, ExecutionCheckpoint] = {}

    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        self._checkpoints[checkpoint.execution_id] = checkpoint.model_copy(deep=True)

    def load(self, execution_id: str) -> ExecutionCheckpoint | None:
        checkpoint = self._checkpoints.get(execution_id)
        return checkpoint.model_copy(deep=True) if checkpoint else None

    def exists(self, execution_id: str) -> bool:
        return execution_id in self._checkpoints

    def delete(self, execution_id: str) -> None:
        self._checkpoints.pop(execution_id, None)


class SQLiteCheckpointStore:
    

    def __init__(self, db_path: str = "runtime_checkpoints.db"):
        self._db_path = db_path
        self._init_table()

    def _connect(self):
        return sqlite3.connect(self._db_path)

    def _init_table(self):
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS runtime_checkpoints ("
                "execution_id TEXT PRIMARY KEY, data TEXT NOT NULL)"
            )

    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runtime_checkpoints (execution_id, data) VALUES (?, ?) "
                "ON CONFLICT(execution_id) DO UPDATE SET data = excluded.data",
                (checkpoint.execution_id, checkpoint.model_dump_json()),
            )

    def load(self, execution_id: str) -> ExecutionCheckpoint | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM runtime_checkpoints WHERE execution_id = ?", (execution_id,)
            ).fetchone()
        if row is None:
            return None
        try:
            return ExecutionCheckpoint.model_validate_json(row[0])
        except ValidationError as exc:
            # a row exists but its content is unreadable — genuinely
            # corrupt, distinct from "no row" (that's just None above)
            raise CheckpointCorruptError(execution_id, str(exc)) from exc

    def exists(self, execution_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM runtime_checkpoints WHERE execution_id = ?", (execution_id,)
            ).fetchone()
        return row is not None

    def delete(self, execution_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM runtime_checkpoints WHERE execution_id = ?", (execution_id,))


class CheckpointManager:
    """The only thing AgentRuntime talks to for checkpointing — never a
    store directly. Owns snapshot creation, schema versioning, and
    validation on restore. Does not execute tools, run the planner, or
    perform reflection."""

    def __init__(
        self,
        store: CheckpointStore | None = None,
        schema_version: int = CHECKPOINT_SCHEMA_VERSION,
    ):
        self._store = store or InMemoryCheckpointStore()
        self._schema_version = schema_version

    def checkpoint(
        self,
        context: "RuntimeContext",
        retry_counts: dict[str, int],
        current_step: str | None,
        status: ExecutionStatus,
        created_at: float,
        resume_count: int = 0,
    ) -> ExecutionCheckpoint:
        
        now = time.time()
        snapshot = ExecutionCheckpoint(
            schema_version=self._schema_version,
            checkpoint_id=str(uuid.uuid4()),
            execution_id=context.trace_id,
            session_id=context.state.session_id,
            agent=context.agent_name,
            status=status,
            plan_state=[RuntimeStepSnapshot.from_step(s) for s in context.state.plan],
            completed_steps=[s.name for s in context.state.plan if s.completed],
            current_step=current_step,
            retry_counts=dict(retry_counts),
            working_memory=dict(context.state.working_memory.variables),
            runtime_metadata={"query": context.state.query, "user_id": context.state.user_id},
            resume_count=resume_count,
            created_at=created_at,
            updated_at=now,
        )
        self._store.save(snapshot)
        return snapshot

    def restore(
        self, execution_id: str, session_id: str, agent_name: str | None = None
    ) -> ExecutionCheckpoint:
        checkpoint = self._store.load(execution_id)
        if checkpoint is None:
            raise CheckpointNotFoundError(execution_id)
        if checkpoint.schema_version != self._schema_version:
            raise CheckpointVersionError(checkpoint.schema_version, self._schema_version)
        if checkpoint.session_id != session_id:
            raise CheckpointIdentityMismatchError(execution_id, session_id, checkpoint.session_id)
        if agent_name is not None and checkpoint.agent != agent_name:
            raise CheckpointAgentMismatchError(execution_id, agent_name, checkpoint.agent)
        return checkpoint

    def exists(self, execution_id: str) -> bool:
        return self._store.exists(execution_id)

    def delete(self, execution_id: str) -> None:
        self._store.delete(execution_id)
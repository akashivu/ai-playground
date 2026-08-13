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
    RuntimeStepSnapshot,
)
from langchain_components.runtime.exceptions import (
    CheckpointCorruptError,
    CheckpointIdentityMismatchError,
    CheckpointNotFoundError,
    CheckpointVersionError,
)

if TYPE_CHECKING:
    from langchain_components.runtime.context import RuntimeContext


logger = logging.getLogger(__name__)


class CheckpointStore(Protocol):
    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        ...

    def load(self, execution_id: str) -> ExecutionCheckpoint | None:
        ...

    def exists(self, execution_id: str) -> bool:
        ...

    def delete(self, execution_id: str) -> None:
        ...


class InMemoryCheckpointStore:
    """
    Development/test checkpoint store.

    Not durable across process restarts.
    """

    def __init__(self) -> None:
        self._checkpoints: dict[str, ExecutionCheckpoint] = {}

    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        self._checkpoints[checkpoint.execution_id] = checkpoint.model_copy(
            deep=True
        )

    def load(self, execution_id: str) -> ExecutionCheckpoint | None:
        checkpoint = self._checkpoints.get(execution_id)

        if checkpoint is None:
            return None

        return checkpoint.model_copy(deep=True)

    def exists(self, execution_id: str) -> bool:
        return execution_id in self._checkpoints

    def delete(self, execution_id: str) -> None:
        self._checkpoints.pop(execution_id, None)


class SQLiteCheckpointStore:
    

    def __init__(self, db_path: str = "runtime_checkpoints.db") -> None:
        self._db_path = db_path
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self._db_path,
            timeout=10,
        )

    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_checkpoints (
                    execution_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )

    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        payload = checkpoint.model_dump_json()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runtime_checkpoints (
                    execution_id,
                    data
                )
                VALUES (?, ?)
                ON CONFLICT(execution_id)
                DO UPDATE SET data = excluded.data
                """,
                (
                    checkpoint.execution_id,
                    payload,
                ),
            )

    def load(self, execution_id: str) -> ExecutionCheckpoint | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT data
                FROM runtime_checkpoints
                WHERE execution_id = ?
                """,
                (execution_id,),
            ).fetchone()

        if row is None:
            return None

        try:
            return ExecutionCheckpoint.model_validate_json(row[0])

        except ValidationError as exc:
            raise CheckpointCorruptError(
                execution_id,
                str(exc),
            ) from exc

    def exists(self, execution_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM runtime_checkpoints
                WHERE execution_id = ?
                """,
                (execution_id,),
            ).fetchone()

        return row is not None

    def delete(self, execution_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                DELETE FROM runtime_checkpoints
                WHERE execution_id = ?
                """,
                (execution_id,),
            )


class CheckpointManager:
    

    def __init__(
        self,
        store: CheckpointStore | None = None,
        schema_version: int = CHECKPOINT_SCHEMA_VERSION,
    ) -> None:
        self._store = store or InMemoryCheckpointStore()
        self._schema_version = schema_version

    def checkpoint(
        self,
        context: "RuntimeContext",
        retry_counts: dict[str, int],
        current_step: str | None,
        pending_user_input: str | None = None,
    ) -> ExecutionCheckpoint:
        now = time.time()

        existing = self._store.load(context.trace_id)

        created_at = (
            existing.created_at
            if existing is not None
            else now
        )

        runtime_metadata = {
            "query": context.state.query,
            "user_id": context.state.user_id,
            "pending_user_input": pending_user_input,
        }

        snapshot = ExecutionCheckpoint(
            schema_version=self._schema_version,
            checkpoint_id=str(uuid.uuid4()),
            execution_id=context.trace_id,
            session_id=context.state.session_id,
            agent=context.agent_name,
            plan_state=[
                RuntimeStepSnapshot.from_step(step)
                for step in context.state.plan
            ],
            completed_steps=[
                step.name
                for step in context.state.plan
                if step.completed
            ],
            current_step=current_step,
            retry_counts=dict(retry_counts),
            working_memory=dict(
                context.state.working_memory.variables
            ),
            runtime_metadata=runtime_metadata,
            created_at=created_at,
            updated_at=now,
        )

        self._store.save(snapshot)

        logger.info(
            "checkpoint saved execution=%s step=%s",
            context.trace_id,
            current_step,
        )

        return snapshot

    def restore(
        self,
        execution_id: str,
        session_id: str,
    ) -> ExecutionCheckpoint:
        checkpoint = self._store.load(execution_id)

        if checkpoint is None:
            raise CheckpointNotFoundError(execution_id)

        if checkpoint.schema_version != self._schema_version:
            raise CheckpointVersionError(
                checkpoint.schema_version,
                self._schema_version,
            )

        if checkpoint.session_id != session_id:
            raise CheckpointIdentityMismatchError(
                execution_id,
                session_id,
                checkpoint.session_id,
            )

        return checkpoint

    def exists(self, execution_id: str) -> bool:
        return self._store.exists(execution_id)

    def delete(self, execution_id: str) -> None:
        self._store.delete(execution_id)
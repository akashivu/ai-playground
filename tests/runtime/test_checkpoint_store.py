from pathlib import Path

from langchain_components.runtime.checkpoint import (
    InMemoryCheckpointStore,
    SQLiteCheckpointStore,
)
from langchain_components.runtime.checkpoint_models import (
    ExecutionCheckpoint,
)


def make_checkpoint() -> ExecutionCheckpoint:
    return ExecutionCheckpoint(
        checkpoint_id="checkpoint-1",
        execution_id="execution-1",
        session_id="session-1",
        agent="booking",
        plan_state=[],
        completed_steps=[],
        current_step=None,
        retry_counts={"step_1": 1},
        working_memory={
            "pickup": "airport",
        },
        runtime_metadata={},
        created_at=1.0,
        updated_at=2.0,
    )


def test_in_memory_store_round_trip():
    store = InMemoryCheckpointStore()

    checkpoint = make_checkpoint()

    store.save(checkpoint)

    restored = store.load(
        "execution-1"
    )

    assert restored is not None
    assert restored.execution_id == "execution-1"
    assert restored.retry_counts["step_1"] == 1


def test_in_memory_store_delete():
    store = InMemoryCheckpointStore()

    store.save(make_checkpoint())

    assert store.exists(
        "execution-1"
    )

    store.delete(
        "execution-1"
    )

    assert not store.exists(
        "execution-1"
    )


def test_sqlite_store_round_trip(
    tmp_path: Path,
):
    db_path = tmp_path / "checkpoints.db"

    store = SQLiteCheckpointStore(
        db_path=str(db_path)
    )

    checkpoint = make_checkpoint()

    store.save(checkpoint)

    restored = store.load(
        "execution-1"
    )

    assert restored is not None
    assert restored.execution_id == "execution-1"
    assert restored.working_memory["pickup"] == "airport"


def test_sqlite_store_delete(
    tmp_path: Path,
):
    db_path = tmp_path / "checkpoints.db"

    store = SQLiteCheckpointStore(
        db_path=str(db_path)
    )

    store.save(make_checkpoint())

    assert store.exists(
        "execution-1"
    )

    store.delete(
        "execution-1"
    )

    assert not store.exists(
        "execution-1"
    )
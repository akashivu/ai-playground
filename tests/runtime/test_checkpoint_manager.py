from types import SimpleNamespace

import pytest

from langchain_components.runtime.checkpoint import (
    CheckpointManager,
    InMemoryCheckpointStore,
)
from langchain_components.runtime.checkpoint_models import (
    ExecutionCheckpoint,
)
from langchain_components.runtime.exceptions import (
    CheckpointIdentityMismatchError,
    CheckpointNotFoundError,
)
from langchain_components.memory.runtime.models import (
    WorkingMemory,
)


def make_context():
    step = SimpleNamespace(
        name="estimate_fare",
        tool_name="estimate_fare",
        payload={"pickup": "airport"},
        description="Estimate fare",
        output=None,
        completed=False,
    )

    state = SimpleNamespace(
        session_id="session-1",
        user_id="user-1",
        query="Book a cab",
        plan=[step],
        working_memory=WorkingMemory(
            variables={
                "pickup": "airport",
            }
        ),
    )

    return SimpleNamespace(
        state=state,
        agent_name="booking_agent",
        trace_id="execution-1",
    )


def test_checkpoint_manager_saves_checkpoint():
    store = InMemoryCheckpointStore()

    manager = CheckpointManager(
        store=store
    )

    context = make_context()

    checkpoint = manager.checkpoint(
        context=context,
        retry_counts={
            "estimate_fare": 1
        },
        current_step="estimate_fare",
    )

    assert checkpoint.execution_id == "execution-1"
    assert checkpoint.session_id == "session-1"
    assert checkpoint.retry_counts[
        "estimate_fare"
    ] == 1


def test_checkpoint_manager_restores_checkpoint():
    store = InMemoryCheckpointStore()

    manager = CheckpointManager(
        store=store
    )

    context = make_context()

    manager.checkpoint(
        context=context,
        retry_counts={},
        current_step="estimate_fare",
    )

    restored = manager.restore(
        execution_id="execution-1",
        session_id="session-1",
    )

    assert restored.execution_id == "execution-1"


def test_missing_checkpoint_raises():
    manager = CheckpointManager(
        store=InMemoryCheckpointStore()
    )

    with pytest.raises(
        CheckpointNotFoundError
    ):
        manager.restore(
            execution_id="missing",
            session_id="session-1",
        )


def test_session_mismatch_raises():
    store = InMemoryCheckpointStore()

    manager = CheckpointManager(
        store=store
    )

    context = make_context()

    manager.checkpoint(
        context=context,
        retry_counts={},
        current_step=None,
    )

    with pytest.raises(
        CheckpointIdentityMismatchError
    ):
        manager.restore(
            execution_id="execution-1",
            session_id="wrong-session",
        )
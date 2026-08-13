from langchain_components.runtime.checkpoint_models import (
    CHECKPOINT_SCHEMA_VERSION,
    ExecutionCheckpoint,
    RuntimeStepSnapshot,
)
from langchain_components.runtime.models import RuntimeStep


def test_runtime_step_snapshot_round_trip():
    step = RuntimeStep(
        name="estimate_fare",
        tool_name="estimate_fare",
        payload={"pickup": "airport"},
        description="Estimate fare",
        output={"amount": 500},
        completed=True,
    )

    snapshot = RuntimeStepSnapshot.from_step(step)

    restored = snapshot.to_runtime_step()

    assert restored.name == step.name
    assert restored.tool_name == step.tool_name
    assert restored.payload == step.payload
    assert restored.description == step.description
    assert restored.output == step.output
    assert restored.completed is True


def test_checkpoint_schema_version():
    checkpoint = ExecutionCheckpoint(
        checkpoint_id="checkpoint-1",
        execution_id="execution-1",
        session_id="session-1",
        agent="booking",
        plan_state=[],
        completed_steps=[],
        current_step=None,
        retry_counts={},
        working_memory={},
        runtime_metadata={},
        created_at=1.0,
        updated_at=1.0,
    )

    assert (
        checkpoint.schema_version
        == CHECKPOINT_SCHEMA_VERSION
    )
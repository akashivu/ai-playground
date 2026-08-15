class AgentRuntimeError(Exception):
    pass


class PlanningError(AgentRuntimeError):
    pass


class ExecutionError(AgentRuntimeError):
    pass


class StepExecutionError(ExecutionError):
    def __init__(self, step: str, message: str, events: list | None = None):
        self.step = step
        self.events = events or []
        super().__init__(f"{step}: {message}")


class ReflectionError(AgentRuntimeError):
    pass


class CheckpointError(AgentRuntimeError):
    pass


class CheckpointNotFoundError(CheckpointError):
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        super().__init__(f"No checkpoint found for execution_id={execution_id!r}")


class CheckpointCorruptError(CheckpointError):
    def __init__(self, execution_id: str, detail: str):
        self.execution_id = execution_id
        self.detail = detail
        super().__init__(f"Checkpoint for execution_id={execution_id!r} is corrupt: {detail}")


class CheckpointVersionError(CheckpointError):
    def __init__(self, found_version: int, expected_version: int):
        self.found_version = found_version
        self.expected_version = expected_version
        super().__init__(
            f"Checkpoint schema version {found_version} is not supported "
            f"(expected {expected_version})"
        )


class CheckpointIdentityMismatchError(CheckpointError):
    def __init__(self, execution_id: str, expected_session_id: str, found_session_id: str):
        self.execution_id = execution_id
        self.expected_session_id = expected_session_id
        self.found_session_id = found_session_id
        super().__init__(
            f"Checkpoint execution_id={execution_id!r} belongs to session "
            f"{found_session_id!r}, not the requested session {expected_session_id!r}"
        )


class CheckpointAgentMismatchError(CheckpointError):
    def __init__(self, execution_id: str, expected_agent: str, found_agent: str):
        self.execution_id = execution_id
        self.expected_agent = expected_agent
        self.found_agent = found_agent
        super().__init__(
            f"Checkpoint execution_id={execution_id!r} belongs to agent "
            f"{found_agent!r}, not the requested agent {expected_agent!r}"
        )
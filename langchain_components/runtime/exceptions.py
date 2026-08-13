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


class AgentRuntimeError(Exception):
    """Base runtime exception."""


class PlanningError(AgentRuntimeError):
    """Planning failed."""


class ExecutionError(AgentRuntimeError):
    """Runtime execution failed."""


class StepExecutionError(ExecutionError):
    """A specific runtime step could not execute."""

    def __init__(
        self,
        step: str,
        message: str,
        events: list | None = None,
    ) -> None:
        self.step = step
        self.events = events or []

        super().__init__(
            f"{step}: {message}"
        )


class ReflectionError(AgentRuntimeError):
    """Reflection failed."""


class CheckpointError(AgentRuntimeError):
    """Base checkpoint exception."""


class CheckpointPersistenceError(CheckpointError):
    """Checkpoint could not be persisted."""

    def __init__(
        self,
        execution_id: str,
        step: str | None,
        detail: str,
    ) -> None:
        self.execution_id = execution_id
        self.step = step
        self.detail = detail

        super().__init__(
            f"Checkpoint persistence failed "
            f"for execution_id={execution_id!r}, "
            f"step={step!r}: {detail}"
        )


class CheckpointNotFoundError(CheckpointError):
    """Requested checkpoint does not exist."""

    def __init__(self, execution_id: str) -> None:
        self.execution_id = execution_id

        super().__init__(
            f"No checkpoint found for execution_id={execution_id!r}"
        )


class CheckpointCorruptError(CheckpointError):
    """Checkpoint exists but cannot be decoded."""

    def __init__(
        self,
        execution_id: str,
        detail: str,
    ) -> None:
        self.execution_id = execution_id
        self.detail = detail

        super().__init__(
            f"Checkpoint for execution_id={execution_id!r} "
            f"is corrupt: {detail}"
        )


class CheckpointVersionError(CheckpointError):
    """Checkpoint schema version is unsupported."""

    def __init__(
        self,
        found_version: int,
        expected_version: int,
    ) -> None:
        self.found_version = found_version
        self.expected_version = expected_version

        super().__init__(
            f"Checkpoint schema version {found_version} "
            f"is not supported "
            f"(expected {expected_version})"
        )


class CheckpointIdentityMismatchError(CheckpointError):
    """Checkpoint belongs to another session."""

    def __init__(
        self,
        execution_id: str,
        expected_session_id: str,
        found_session_id: str,
    ) -> None:
        self.execution_id = execution_id
        self.expected_session_id = expected_session_id
        self.found_session_id = found_session_id

        super().__init__(
            f"Checkpoint execution_id={execution_id!r} "
            f"belongs to session {found_session_id!r}, "
            f"not the requested session "
            f"{expected_session_id!r}"
        )
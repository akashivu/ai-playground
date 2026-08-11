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
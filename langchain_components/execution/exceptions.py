from __future__ import annotations


class ExecutionEngineError(Exception):
    pass


class PlanValidationError(ExecutionEngineError):
    def __init__(self, detail: str):
        super().__init__(f"Invalid execution plan: {detail}")
        self.detail = detail


class StepDependencyError(ExecutionEngineError):
    def __init__(self, step_id: str, depends_on: list[str]):
        super().__init__(
            f"Step '{step_id}' cannot run - its dependencies {depends_on} were not satisfied"
        )
        self.step_id = step_id
        self.depends_on = depends_on
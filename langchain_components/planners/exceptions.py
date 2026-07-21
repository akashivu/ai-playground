from __future__ import annotations


class PlannerError(Exception):
    pass


class PlannerNotFoundError(PlannerError):
    def __init__(self, name: str):
        super().__init__(f"Planner '{name}' is not registered.")
        self.name = name


class PlannerAlreadyRegisteredError(PlannerError):
    def __init__(self, name: str):
        super().__init__(f"Planner '{name}' is already registered.")
        self.name = name


class PlanValidationError(PlannerError):
    def __init__(self, planner_name: str, detail: str):
        super().__init__(f"Planner '{planner_name}' produced an invalid plan: {detail}")
        self.planner_name = planner_name
        self.detail = detail


class PlanningFailedError(PlannerError):
    def __init__(self, planner_name: str, detail: str):
        super().__init__(f"Planner '{planner_name}' failed to produce a plan: {detail}")
        self.planner_name = planner_name
        self.detail = detail
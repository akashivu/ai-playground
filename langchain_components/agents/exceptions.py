from __future__ import annotations


class AgentError(Exception):
    pass


class AgentNotFoundError(AgentError):
    def __init__(self, name: str):
        super().__init__(f"Agent '{name}' is not registered.")
        self.name = name


class AgentAlreadyRegisteredError(AgentError):
    def __init__(self, name: str):
        super().__init__(f"Agent '{name}' is already registered.")
        self.name = name


class PlanningError(AgentError):
    def __init__(self, agent_name: str, detail: str):
        super().__init__(f"Agent '{agent_name}' failed to plan: {detail}")
        self.agent_name = agent_name
        self.detail = detail


class ExecutionError(AgentError):
    def __init__(self, agent_name: str, detail: str):
        super().__init__(f"Agent '{agent_name}' failed to execute: {detail}")
        self.agent_name = agent_name
        self.detail = detail
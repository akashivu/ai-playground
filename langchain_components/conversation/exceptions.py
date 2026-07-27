from __future__ import annotations


class ConversationError(Exception):
    pass


class AgentResolutionError(ConversationError):
    def __init__(self, detail: str):
        super().__init__(f"Could not resolve an agent for this request: {detail}")
        self.detail = detail
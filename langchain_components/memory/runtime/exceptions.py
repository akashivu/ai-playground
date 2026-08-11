class AgentMemoryError(Exception):
    pass


class MemoryLoadError(AgentMemoryError):
    pass


class MemorySaveError(AgentMemoryError):
    pass
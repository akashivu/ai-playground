from langchain_components.memory.runtime.models import WorkingMemory


def new_working_memory() -> WorkingMemory:
    return WorkingMemory()
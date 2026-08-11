from langchain_components.memory.runtime.long_term_memory import LongTermMemoryStore
from langchain_components.memory.runtime.session_memory import SessionMemoryStore
from langchain_components.memory.runtime.working_memory import new_working_memory
from langchain_components.runtime.state import RuntimeState
from langchain_components.tools.schemas import ToolResult


class MemoryManager:
    def __init__(self, session_store=None, long_term_store=None):
        self._session_store = session_store or SessionMemoryStore()
        self._long_term_store = long_term_store or LongTermMemoryStore()

    def load(self, state: RuntimeState) -> None:
        state.session_memory = self._session_store.load(state.session_id)
        state.long_term_memory = self._long_term_store.load(state.user_id)
        state.working_memory = new_working_memory()

    def save(self, state: RuntimeState) -> None:
        state.session_memory.variables.update(state.working_memory.variables)
        self._session_store.save(state.session_memory)
        self._long_term_store.save(state.long_term_memory)
        

    def save_tool_result(self, state: RuntimeState, tool_result: ToolResult) -> None:
        
        if not tool_result.success:
            return

        if isinstance(tool_result.data, dict):
            state.working_memory.variables.update(tool_result.data)
        else:
            state.working_memory.variables[tool_result.tool_name] = tool_result.data

    def clear(self, state: RuntimeState) -> None:
        self._session_store.clear(state.session_id)
        self._long_term_store.clear(state.user_id)
from langchain_core.messages import ToolMessage
from langchain_components.agents.tool_executor import execute_tool_call


def tool_node(state: dict) -> dict:
    """Executes tool calls and appends results to message history."""
    messages = state["messages"].copy()
    tool_results = []

    for tool_call in state["tool_calls"]:
        result = execute_tool_call(tool_call)
        tool_results.append(str(result))
        messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
        ))

    return {
        "messages": messages,
        "tool_result": "\n\n".join(tool_results),
    }
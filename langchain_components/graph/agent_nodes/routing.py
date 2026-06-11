from langgraph.graph import END


def route_agent(state: dict) -> str:
    """Routes to tool execution or END based on tool calls and iteration limit."""
    if state.get("iterations", 0) >= state.get("max_iterations", 10):
        return END
    if state.get("tool_calls"):
        return "tool"
    return END
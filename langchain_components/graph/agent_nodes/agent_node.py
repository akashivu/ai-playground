from langchain_components.agents.knowledge_base_agent import knowledge_base_agent


def agent_node(state: dict) -> dict:
    """Invokes the agent and captures response and tool calls."""
    response = knowledge_base_agent.invoke(state["messages"])
    return {
        "answer": response.content,
        "tool_calls": response.tool_calls,
        "messages": state["messages"] + [response],
        "iterations": state.get("iterations", 0) + 1,
    }
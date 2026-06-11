from langchain_core.messages import HumanMessage, ToolMessage
from langchain_components.agents.knowledge_base_agent import agent_llm
from langchain_components.agents.tool_executor import execute_tool_call


def run_agent(question: str) -> str:
    """Runs a single-turn agent workflow with tool execution."""
    messages = [HumanMessage(content=question)]

    response = agent_llm.invoke(messages)

    if not response.tool_calls:
        return response.content

    messages.append(response)

    for tool_call in response.tool_calls:
        result = execute_tool_call(tool_call)
        messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
        ))

    return agent_llm.invoke(messages).content
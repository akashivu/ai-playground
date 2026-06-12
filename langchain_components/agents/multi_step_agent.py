from langchain_core.messages import HumanMessage, ToolMessage
from langchain_components.agents.knowledge_base_agent import knowledge_base_agent
from langchain_components.agents.tool_executor import execute_tool_call


def run_multi_step_agent(question: str, max_iterations: int = 10) -> str:
    """Runs the agent in a loop until no tool calls remain or max iterations reached."""
    messages = [HumanMessage(content=question)]

    for _ in range(max_iterations):
        response = knowledge_base_agent.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            result = execute_tool_call(tool_call)
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            ))

    return "Maximum iterations reached without a final answer."
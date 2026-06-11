from langchain_core.messages import HumanMessage
from langchain_components.graph.agent_graph import agent_graph


def run_agent_graph(question: str, max_iterations: int = 10) -> dict:
    """Runs the agent graph for a given question and returns the final state."""
    initial_state = {
        "question": question,
        "messages": [HumanMessage(content=question)],
        "tool_calls": [],
        "tool_result": "",
        "answer": "",
        "iterations": 0,
        "max_iterations": max_iterations,
    }

    final_state = agent_graph.invoke(initial_state)

    return {
        "question": final_state["question"],
        "answer": final_state["answer"],
        "tool_result": final_state["tool_result"],
        "iterations": final_state["iterations"],
    }
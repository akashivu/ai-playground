from langchain_core.messages import (HumanMessage,)
from langchain_components.agents.knowledge_base_agent import (agent_llm,)

def execute_agent(question: str,):
    """Executes the agent for a user question."""

    response = (
        agent_llm.invoke(
            [
                HumanMessage(
                    content=question
                )
            ]
        )
    )

    return response
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from domains.domain_manager import get_system_prompt
from config.llm_config import get_llm


llm = get_llm(temperature=0.7)


@register_workflow(IntentType.GENERAL)
def general_chat_workflow(state: dict) -> dict:
    """Handles conversational requests with domain personality and session memory."""
    messages = [SystemMessage(content=get_system_prompt())]

    for item in state.get("history", []):
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        elif item["role"] == "assistant":
            messages.append(AIMessage(content=item["content"]))

    messages.append(HumanMessage(content=state["question"]))

    response = llm.invoke(messages)
    return {"answer": response.content}
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from domains.domain_manager import get_system_prompt
from config.llm_config import get_llm


llm = get_llm(temperature=0.7)


@register_workflow(IntentType.GENERAL)
def general_chat_workflow(state: dict) -> dict:
    """Handles general conversational requests with domain personality."""
    response = llm.invoke([
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=state["question"]),
    ])
    return {"answer": response.content}
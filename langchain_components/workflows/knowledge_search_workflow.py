from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.graph.agentic_rag_nodes import agentic_rag_graph
from config.workflow_config import MAX_RAG_RETRIES


@register_workflow(IntentType.KNOWLEDGE_SEARCH)
def knowledge_search_workflow(state: dict) -> dict:
    """Routes knowledge search queries through the agentic RAG graph."""
    result = agentic_rag_graph.invoke({
        "question": state["question"],
        "retry_count": 0,
        "max_retries": MAX_RAG_RETRIES,
    })
    return {"answer": result.get("answer", "")}
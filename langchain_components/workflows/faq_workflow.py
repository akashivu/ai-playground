from langchain_components.registry.workflow_decorator import (register_workflow,)
from langchain_components.routing.intent_types import (IntentType,)
from langchain_components.runnables.hybrid_search_pipeline import (hybrid_search_pipeline,)
from services.retrieval_validator import (RetrievalValidator,)
from langchain_components.chains.rag_answer_chain import rag_answer_chain

@register_workflow(IntentType.FAQ)
def faq_workflow(state: dict) -> dict:
    """
    Handles FAQ requests using
    retrieval-based search.
    """

    results = hybrid_search_pipeline.invoke(
        {
            "query": state["question"],
            "collection": "elixway",
        })

    validation = (RetrievalValidator.validate(results))

    if not validation.is_valid:
        return { "answer": ( "I couldn't find a matching FAQ. " "Please contact Elixway support.")}
    context = "\n\n".join(
    item["chunk"]
    for item in results[:3]
    )

    answer = rag_answer_chain.invoke(
    {
        "question": state["question"],
        "context": context,
    }
    )

    return {
    "answer": answer,
    }
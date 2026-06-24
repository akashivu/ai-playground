from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline
from services.retrieval_validator import RetrievalValidator


@register_workflow(IntentType.POLICY)
def policy_workflow(state: dict) -> dict:
    """Retrieves policy information from the adiyogicabz_policy knowledge collection."""
    results = hybrid_search_pipeline.invoke({
        "query": state["question"],
        "collection": "adiyogicabz_policy",
    })

    validation = RetrievalValidator.validate(results)
    if not validation.is_valid:
        return {
            "answer": (
                "I couldn't find a matching policy. "
                "Please contact AdiyogiCabz support for policy details."
            )
        }

    return {"answer": results[0]["chunk"]}
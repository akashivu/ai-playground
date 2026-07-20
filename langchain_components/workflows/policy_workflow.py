from langchain_components.registry.workflow_decorator import register_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline
from langchain_components.chains.policy_chain import policy_chain
from services.retrieval_validator import RetrievalValidator


@register_workflow(IntentType.POLICY)
def policy_workflow(state: dict) -> dict:
    """Retrieves policy information from the adiyogicabz_policy knowledge collection
    and generates a grounded, natural-language answer via the policy_chain."""
    print("========== POLICY WORKFLOW EXECUTED ==========")
    print("STATE:", state)

    results = hybrid_search_pipeline.invoke({
        "query": state["question"],
        "collection": "adiyogicabz_policy",
    })

    print("QUESTION:", state["question"])
    print("RESULTS:", results)

    validation = RetrievalValidator.validate(results)
    if not validation.is_valid:
        return {
            "answer": (
                "I couldn't find a matching policy. "
                "Please contact AdiyogiCabz support for policy details."
            )
        }

    context = "\n\n".join(result["chunk"] for result in results[:3])

    response = policy_chain.invoke({
        "context": context,
        "question": state["question"],
    })

    return {
        "answer": response.content,
    }
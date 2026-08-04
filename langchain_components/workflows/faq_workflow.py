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
        }
    )

    print("========== FAQ RESULTS ==========")
    for i, item in enumerate(results, 1):
        print(f"\nResult {i}")
        print("Source:", item["source"])
        print(item["chunk"][:500])

    validation = RetrievalValidator.validate(results)

    if not validation.is_valid:
        return {
            "answer": (
                "I couldn't find a matching FAQ. "
                "Please contact Elixway support."
            )
        }

    context = "\n\n".join(item["chunk"] for item in results[:6])

    print("\n========== CONTEXT ==========")
    print(context)

    answer = rag_answer_chain.invoke(
        {
            "question": state["question"],
            "context": context,
        }
    )

    print("\n========== LLM ANSWER ==========")
    print(answer)

    return {
        "answer": answer,
    }
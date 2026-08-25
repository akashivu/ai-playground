from __future__ import annotations

from langchain_components.chains.destination_recommendation_chain import (
    destination_recommendation_chain,
)


class DestinationRecommendationService:
    """
    Temporary India-only destination recommendation service.

    The current implementation delegates recommendation generation to the
    LLM. This abstraction allows a future destination knowledge base or
    recommendation engine to be introduced without changing the workflow.
    """

    def recommend(
        self,
        question: str,
    ) -> str:
        normalized_question = (
            str(
                question or ""
            ).strip()
        )

        if not normalized_question:
            return (
                "Tell me what kind of trip you would like, "
                "and I can suggest Indian destinations."
            )

        result = destination_recommendation_chain.invoke(
            {
                "question": normalized_question,
            }
        )

        return str(result)


destination_recommendation_service = (
    DestinationRecommendationService()
)
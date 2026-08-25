from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievalValidationResult:
    is_valid: bool
    reason: str | None = None


class RetrievalValidator:
    """
    Validates retrieved knowledge results.

    Hybrid retrieval results contain a normalized `rerank_score`
    where higher means more relevant.

    Legacy vector-only results may still contain `score` where
    lower values represent better distance.
    """

    MAX_DISTANCE = 1.5
    MIN_RERANK_SCORE = 0.30

    @classmethod
    def validate(
        cls,
        results: list[dict],
    ) -> RetrievalValidationResult:
        """
        Validate retrieval results according to their scoring model.
        """

        if not results:
            return RetrievalValidationResult(
                is_valid=False,
                reason="NO_RESULTS",
            )

        # -----------------------------------------------------
        # HYBRID / RERANKED RESULTS
        # -----------------------------------------------------

        rerank_scores = []

        for result in results:
            value = result.get("rerank_score")

            if value is None:
                continue

            try:
                rerank_scores.append(
                    float(value)
                )
            except (TypeError, ValueError):
                continue

        if rerank_scores:
            best_relevance = max(
                rerank_scores
            )

            if (
                best_relevance
                < cls.MIN_RERANK_SCORE
            ):
                return RetrievalValidationResult(
                    is_valid=False,
                    reason="LOW_CONFIDENCE",
                )

            return RetrievalValidationResult(
                is_valid=True
            )

        # -----------------------------------------------------
        # LEGACY VECTOR-ONLY RESULTS
        # -----------------------------------------------------

        distances = []

        for result in results:
            value = result.get("score")

            if value is None:
                continue

            try:
                distances.append(
                    float(value)
                )
            except (TypeError, ValueError):
                continue

        if not distances:
            return RetrievalValidationResult(
                is_valid=False,
                reason="NO_VALID_SCORES",
            )

        best_distance = min(distances)

        if best_distance > cls.MAX_DISTANCE:
            return RetrievalValidationResult(
                is_valid=False,
                reason="LOW_CONFIDENCE",
            )

        return RetrievalValidationResult(
            is_valid=True
        )


def fallback_response() -> str:
    """Returns a safe fallback message when retrieval validation fails."""

    return (
        "I couldn't find information about that in the "
        "Elixway knowledge base."
    )
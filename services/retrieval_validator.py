from dataclasses import dataclass


@dataclass
class RetrievalValidationResult:
    is_valid: bool
    reason: str | None = None


class RetrievalValidator:
    """Fast retrieval quality check before expensive LLM relevance evaluation."""

    MAX_DISTANCE = 1.5

    @classmethod
    def validate(cls, results: list[dict]) -> RetrievalValidationResult:
        """Validates retrieval results based on presence and distance score."""
        if not results:
            return RetrievalValidationResult(is_valid=False, reason="NO_RESULTS")

        best_distance = min(result["score"] for result in results)
        if best_distance > cls.MAX_DISTANCE:
            return RetrievalValidationResult(is_valid=False, reason="LOW_CONFIDENCE")

        return RetrievalValidationResult(is_valid=True)


def fallback_response() -> str:
    """Returns the safe fallback message when retrieval validation fails."""
    return "I couldn't find information about that in the Elixway knowledge base."


from __future__ import annotations

import logging

from .models import RetrievalResult

logger = logging.getLogger(__name__)


DEFAULT_MIN_FUSION_SCORE = 0.01


class RetrievalValidator:
    def __init__(
        self,
        min_fusion_score: float = DEFAULT_MIN_FUSION_SCORE,
        top_k: int = 5,
    ):
        self.min_fusion_score = min_fusion_score
        self.top_k = top_k

    def validate(
        self,
        results: list[RetrievalResult],
        category: str | None = None,
    ) -> list[RetrievalResult]:
        validated: list[RetrievalResult] = []
        seen_text: set[str] = set()

        for result in results:
            if category is not None and result.category != category:
                logger.debug(
                    "Dropping result %r: category %r != requested %r",
                    result.title, result.category, category,
                )
                continue

            if result.fusion_score < self.min_fusion_score:
                logger.debug(
                    "Dropping result %r: fusion_score %.4f below threshold %.4f",
                    result.title, result.fusion_score, self.min_fusion_score,
                )
                continue

            if result.chunk in seen_text:
                continue
            seen_text.add(result.chunk)

            validated.append(result)
            if len(validated) >= self.top_k:
                break

        if not validated:
            logger.warning("No results survived validation")

        return validated

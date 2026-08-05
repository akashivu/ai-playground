
from __future__ import annotations

from .models import RetrievalResult


class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        vector_results: list[RetrievalResult],
        bm25_results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        merged: dict[tuple[str, int], RetrievalResult] = {}

        for result in vector_results:
            merged[result.key] = result

        for result in bm25_results:
            if result.key in merged:
                existing = merged[result.key]
                existing.bm25_rank = result.bm25_rank
                existing.bm25_score = result.bm25_score
            else:
                merged[result.key] = result

        for result in merged.values():
            fusion_score = 0.0
            if result.vector_rank is not None:
                fusion_score += 1.0 / (self.k + result.vector_rank)
            if result.bm25_rank is not None:
                fusion_score += 1.0 / (self.k + result.bm25_rank)
            result.fusion_score = fusion_score

        return sorted(merged.values(), key=lambda r: r.fusion_score, reverse=True)

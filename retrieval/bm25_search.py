

from __future__ import annotations

from rank_bm25 import BM25Okapi

from ingestion.models import KnowledgeChunk
from .models import RetrievalResult
from .vector_search import _chunk_to_result, _tokenize


class BM25Search:
    def __init__(self, chunks: list[KnowledgeChunk]):
        self.chunks = chunks
        self._tokenized = [_tokenize(c.text) for c in chunks]
        self._bm25 = BM25Okapi(self._tokenized) if self._tokenized else None

    def search(
        self, query: str, top_k: int = 20, category: str | None = None
    ) -> list[RetrievalResult]:
        if self._bm25 is None:
            return []

        query_tokens = _tokenize(query)
        scores = self._bm25.get_scores(query_tokens)

        scored = [
            (chunk, score)
            for chunk, score in zip(self.chunks, scores)
            if score > 0 and (category is None or chunk.category == category)
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        results = []
        for rank, (chunk, score) in enumerate(scored[:top_k], start=1):
            result = _chunk_to_result(chunk, score, rank)
            # this came from BM25, not vector search — relabel the rank/score fields
            result.vector_rank, result.vector_score = None, None
            result.bm25_rank, result.bm25_score = rank, score
            results.append(result)
        return results

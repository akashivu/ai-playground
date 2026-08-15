

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol

from ingestion.models import KnowledgeChunk
from .models import RetrievalResult

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class VectorSearcher(Protocol):
    def search(
        self, query: str, top_k: int = 20, category: str | None = None
    ) -> list[RetrievalResult]: ...


def _chunk_to_result(chunk: KnowledgeChunk, score: float, rank: int) -> RetrievalResult:
    return RetrievalResult(
        chunk=chunk.text,
        score=score,
        source=chunk.source,
        collection=chunk.collection,
        category=chunk.category,
        document_id=chunk.document_id,
        title=chunk.title,
        topic=chunk.topic,
        chunk_index=chunk.chunk_index,
        metadata=chunk.metadata,
        vector_rank=rank,
        vector_score=score,
    )


class SimpleVectorSearch:
    

    def __init__(self, chunks: list[KnowledgeChunk]):
        self.chunks = chunks
        self._vectors = [Counter(_tokenize(c.text)) for c in chunks]

    @staticmethod
    def _cosine(a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        shared = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in shared)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(
        self, query: str, top_k: int = 20, category: str | None = None
    ) -> list[RetrievalResult]:
        query_vec = Counter(_tokenize(query))
        scored = []
        for chunk, vec in zip(self.chunks, self._vectors):
            if category and chunk.category != category:
                continue
            score = self._cosine(query_vec, vec)
            if score > 0:
                scored.append((chunk, score))

        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [
            _chunk_to_result(chunk, score, rank)
            for rank, (chunk, score) in enumerate(scored[:top_k], start=1)
        ]

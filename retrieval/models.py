

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalResult:
    chunk: str
    score: float
    source: str
    collection: str
    category: str
    document_id: str
    title: str
    topic: str
    chunk_index: int = 0
    metadata: dict = field(default_factory=dict)

    # Ranking provenance — populated as the result moves through the pipeline
    vector_rank: int | None = None
    vector_score: float | None = None
    bm25_rank: int | None = None
    bm25_score: float | None = None
    fusion_score: float = 0.0
    rerank_score: float | None = None

    @property
    def key(self) -> tuple[str, int]:
        """Identity used to merge the same chunk seen from two retrievers."""
        return (self.document_id, self.chunk_index)

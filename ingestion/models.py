

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class KnowledgeDocument:
    source: Path
    collection: str
    category: str          # "faq" | "policy" | "pricing" | "vehicle" | "city"
    title: str
    content: str

    @property
    def document_id(self) -> str:
        return self.source.stem  # e.g. "pet_policy"


@dataclass(slots=True)
class KnowledgeChunk:
    text: str
    source: str
    collection: str
    category: str
    title: str              # section-level title, e.g. "PET POLICY" or the FAQ question
    chunk_index: int
    document_id: str
    topic: str = ""          # short slug derived from title, used for metadata filtering
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Flat dict ready to hand to an embedding/vector-store call."""
        return {
            "text": self.text,
            "collection": self.collection,
            "category": self.category,
            "title": self.title,
            "topic": self.topic,
            "source": self.source,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            **self.metadata,
        }

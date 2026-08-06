

from __future__ import annotations

from ingestion.models import KnowledgeChunk


REQUIRED_FIELDS = ("collection", "category", "topic", "source", "document_id")


def build_metadata(chunk: KnowledgeChunk) -> dict:
    metadata = {
        "collection": chunk.collection,
        "category": chunk.category,
        "topic": chunk.topic,
        "title": chunk.title,
        "source": chunk.source,
        "document_id": chunk.document_id,
        "chunk_index": chunk.chunk_index,
    }
    missing = [f for f in REQUIRED_FIELDS if not metadata.get(f)]
    if missing:
        raise ValueError(
            f"Chunk from {chunk.source} (index {chunk.chunk_index}) "
            f"is missing required metadata fields: {missing}"
        )
    return metadata


def attach_metadata(chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
    """Validate + freeze metadata onto each chunk, in place, and return them."""
    for chunk in chunks:
        chunk.metadata = build_metadata(chunk)
    return chunks

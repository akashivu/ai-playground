

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from .metadata_builder import attach_metadata
from .models import KnowledgeChunk
from .parser import parse_directory
from .section_splitter import split_document
from .validators import validate_chunks

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IngestionReport:
    
    collection: str
    documents: int
    chunks: int
    embedding_model: str
    timestamp: str

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


class Embedder(Protocol):
    
    model_name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def build_chunks(knowledge_root: Path, collection: str) -> list[KnowledgeChunk]:
    
    documents = parse_directory(knowledge_root, collection)
    logger.info("Parsed %d documents from %s", len(documents), knowledge_root)

    all_chunks: list[KnowledgeChunk] = []
    for doc in documents:
        doc_chunks = split_document(doc)
        all_chunks.extend(doc_chunks)
    logger.info("Split into %d raw chunks", len(all_chunks))

    attach_metadata(all_chunks)
    clean_chunks = validate_chunks(all_chunks)
    logger.info(
        "%d chunks passed validation (%d dropped)",
        len(clean_chunks), len(all_chunks) - len(clean_chunks),
    )

    return clean_chunks


def embed_and_index(
    chunks: list[KnowledgeChunk],
    embedder: Embedder,
    index_builder: Callable[[list[list[float]], list[dict]], object],
) -> object:
    
    texts = [c.text for c in chunks]
    vectors = embedder.embed(texts)
    metadatas = [c.metadata for c in chunks]
    return index_builder(vectors, metadatas)


def run_ingestion(
    knowledge_root: Path,
    collection: str,
    embedder: Embedder | None = None,
    index_builder: Callable[[list[list[float]], list[dict]], object] | None = None,
    report_path: Path | None = None,
) -> tuple[list[KnowledgeChunk], object | None]:
    
    chunks = build_chunks(knowledge_root, collection)

    index = None
    if embedder is not None and index_builder is not None:
        index = embed_and_index(chunks, embedder, index_builder)

    report = IngestionReport(
        collection=collection,
        documents=len({c.document_id for c in chunks}),
        chunks=len(chunks),
        embedding_model=embedder.model_name if embedder else "none (dry run)",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    if report_path:
        report.save(report_path)
        logger.info("Wrote ingestion report to %s", report_path)
    else:
        logger.info("Ingestion report: %s", asdict(report))

    return chunks, index

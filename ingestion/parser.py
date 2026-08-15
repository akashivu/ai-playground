

from __future__ import annotations

import logging
from pathlib import Path

from .models import KnowledgeDocument

logger = logging.getLogger(__name__)


CATEGORY_ALIASES = {
    "faq": "faq",
    "faqs": "faq",
    "policies": "policy",
    "policy": "policy",
    "pricing": "pricing",
    "vehicles": "vehicle",
    "vehicle": "vehicle",
    "cities": "city",
    "city": "city",
}


def detect_category(path: Path) -> str:
    folder = path.parent.name.lower()
    return CATEGORY_ALIASES.get(folder, folder)


def extract_title(content: str, fallback: str) -> str:
    
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            if len(stripped) <= 80 and not stripped.endswith("."):
                return stripped
            break
    return fallback


def parse_file(path: Path, collection: str) -> KnowledgeDocument:
    """Parse a single .txt file into a KnowledgeDocument."""
    if not path.exists():
        raise FileNotFoundError(f"Knowledge source not found: {path}")

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        logger.warning("Empty knowledge file skipped: %s", path)

    category = detect_category(path)
    fallback_title = path.stem.replace("_", " ").title()
    title = extract_title(raw, fallback_title)

    return KnowledgeDocument(
        source=path,
        collection=collection,
        category=category,
        title=title,
        content=raw,
    )


def parse_directory(root: Path, collection: str) -> list[KnowledgeDocument]:
   
    documents: list[KnowledgeDocument] = []
    for path in sorted(root.rglob("*.txt")):
        try:
            doc = parse_file(path, collection)
            if doc.content:
                documents.append(doc)
        except Exception as exc:  # noqa: BLE001 - log and continue ingestion
            logger.error("Failed to parse %s: %s", path, exc)
    return documents

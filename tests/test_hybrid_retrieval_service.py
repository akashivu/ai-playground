from services.hybrid_retrieval_service import HybridRetrievalService


class MockVectorService:
    def search(self, query: str, top_k: int = 3, collection: str = None) -> list[dict]:
        return [{"chunk": "Goa package", "source": "goa.pdf", "document_id": "1", "collection": "travel", "score": 0.9}]


class MockBM25Service:
    def search(self, query: str, top_k: int = 3, collection: str = None) -> list[dict]:
        return [
            {"chunk": "Goa package", "source": "goa.pdf", "document_id": "1", "collection": "travel", "score": 0.8},
            {"chunk": "Coorg package", "source": "coorg.pdf", "document_id": "2", "collection": "travel", "score": 0.6},
        ]


def test_merge_deduplicates():
    service = HybridRetrievalService(MockVectorService(), MockBM25Service())
    results = service.search("Goa")
    assert len(results) == 2


def test_merge_preserves_all_unique():
    service = HybridRetrievalService(MockVectorService(), MockBM25Service())
    results = service.search("Goa")
    chunks = [r["chunk"] for r in results]
    assert "Goa package" in chunks
    assert "Coorg package" in chunks


def test_search_passes_collection():
    """Verifies collection parameter is forwarded to both services."""
    received = {}

    class TrackingVectorService:
        def search(self, query, top_k=3, collection=None):
            received["vector_collection"] = collection
            return []

    class TrackingBM25Service:
        def search(self, query, top_k=3, collection=None):
            received["bm25_collection"] = collection
            return []

    service = HybridRetrievalService(TrackingVectorService(), TrackingBM25Service())
    service.search("Goa", collection="travel")

    assert received["vector_collection"] == "travel"
    assert received["bm25_collection"] == "travel"
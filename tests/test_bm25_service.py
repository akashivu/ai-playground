import pytest
from services.bm25_service import BM25Service

SAMPLE_METADATA = [
    {"text": "Goa beach package", "source": "goa.pdf", "document_id": "1", "collection": "travel"},
    {"text": "Coorg hill station package", "source": "coorg.pdf", "document_id": "2", "collection": "travel"},
    {"text": "Mental wellness guide", "source": "wellness.pdf", "document_id": "3", "collection": "health"},
]


@pytest.fixture
def bm25_service():
    service = BM25Service()
    service.build_index(SAMPLE_METADATA)
    return service


def test_search_returns_results(bm25_service):
    results = bm25_service.search("Goa")
    assert len(results) > 0


def test_search_before_build_raises():
    service = BM25Service()
    with pytest.raises(RuntimeError):
        service.search("Goa")


def test_collection_filter_travel(bm25_service):
    results = bm25_service.search(query="Goa", collection="travel")
    assert all(item["collection"] == "travel" for item in results)


def test_collection_filter_excludes_other(bm25_service):
    results = bm25_service.search(query="wellness", collection="travel")
    assert all(item["collection"] == "travel" for item in results)


def test_top_k_respected(bm25_service):
    results = bm25_service.search("package", top_k=1)
    assert len(results) <= 1
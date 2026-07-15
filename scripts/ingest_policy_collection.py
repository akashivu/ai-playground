import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.knowledge_ingestion_service import KnowledgeIngestionService
from core.dependencies import vector_store, bm25_service

knowledge_ingestion_service = KnowledgeIngestionService(
    vector_store=vector_store,
    bm25_service=bm25_service,
)
from utils.logger import logger


def main():
    policy_dir = "langchain_components/knowledge/adiyogicabz_policy"
    collection = "adiyogicabz_policy"

    logger.info(f"Starting policy ingestion from '{policy_dir}' into '{collection}'.")

    total = knowledge_ingestion_service.ingest_directory(
        directory=policy_dir,
        collection=collection,
    )

   
    from core.dependencies import vector_store
    vector_store.save_index("data/faiss_index.bin")
    vector_store.save_metadata("data/metadata.json")

    logger.info(f"Policy ingestion complete. {total} chunks indexed.")


if __name__ == "__main__":
    main()

import sys
import os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from services.knowledge_ingestion_service import (knowledge_ingestion_service,)
from utils.logger import logger
from core.dependencies import vector_store

def main():

    faq_dir = "knowledge/elixway_faq"
    collection = "elixway_faq"
    logger.info(f"Starting FAQ ingestion from " f"'{faq_dir}' into '{collection}'.")
    result = (knowledge_ingestion_service.ingest_directory(directory=faq_dir,collection=collection,))
    vector_store.save_index( "data/faiss_index.bin")
    vector_store.save_metadata("data/metadata.json")
    logger.info( f"FAQ ingestion complete. " f"{result['chunks']} chunks indexed.")


if __name__ == "__main__":
    main()
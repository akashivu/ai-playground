from core.dependencies import knowledge_ingestion_service


def main() -> None:
    result = knowledge_ingestion_service.ingest_directory(
        directory="knowledge",
        collection="elixway",
    )

    print(result)


if __name__ == "__main__":
    main()
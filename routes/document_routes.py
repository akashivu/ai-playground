from uuid import uuid4
from fastapi import APIRouter, File, UploadFile
from core.dependencies import knowledge_ingestion_service
from domains.domain_manager import get_collection_name

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    result = knowledge_ingestion_service.ingest_pdf(
        file_path=file_path,
        document_id=str(uuid4()),
        collection=get_collection_name(),
    )

    return result
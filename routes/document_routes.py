from fastapi import (APIRouter,UploadFile,File,)

from core.dependencies import (document_service,)

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...),):

    file_path = (f"uploads/{file.filename}")

    with open(file_path,"wb",) as buffer:

        buffer.write(await file.read())

    result = (document_service.process_document(file_path))

    return result
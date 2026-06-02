from pydantic import BaseModel


class DocumentRequest(BaseModel):

    document_id: str

    name: str

    collection: str
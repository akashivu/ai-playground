from pydantic import BaseModel


class HybridSearchRequest(BaseModel):

    query: str
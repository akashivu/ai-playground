from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    question: str
    guest_id: str | None = None


class SearchRequest(BaseModel):
    query : str
    top_k : int = 3

class ChatResponse(BaseModel):
    session_id: str
    answer: str

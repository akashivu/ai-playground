from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    question: str


class SearchRequest(BaseModel):
    query : str
    top_k : int = 3
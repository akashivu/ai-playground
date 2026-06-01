from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class SearchRequest(BaseModel):
    query : str
    top_k : int = 3
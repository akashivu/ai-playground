from pydantic import BaseModel


class AIResponse(BaseModel):
    session_id: str
    answer: str
    intent: str | None = None
    completed: bool = False
    metadata: dict | None = None
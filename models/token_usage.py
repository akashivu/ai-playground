from pydantic import BaseModel


class TokenUsage(BaseModel):
    session_id: str
    intent: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
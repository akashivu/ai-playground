from pydantic import BaseModel


class UsageLog(BaseModel):
    session_id: str
    intent: str
    latency: float
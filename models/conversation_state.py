from typing import Optional, Any
from pydantic import BaseModel, field_validator


class ConversationState(BaseModel):
    """
    Represents the current conversation context passed
    through the AI workflow pipeline.
    """
    session_id: str
    user_id: str
    email: Optional[str] = None
    role: str
    question: str
    history: list[dict]
    booking_details: dict
    recommendation_details: dict

    @field_validator("user_id", mode="before")
    @classmethod
    def coerce_user_id_to_str(cls, v: Any) -> str:
        return str(v)

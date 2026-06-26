from pydantic import BaseModel


class ConversationState(BaseModel):
    """
    Represents the current conversation context passed
    through the AI workflow pipeline.
    """

    session_id: str
    user_id: str
    email: str
    role: str

    question: str
    history: list[dict]

    booking_details: dict
    recommendation_details: dict
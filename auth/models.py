from pydantic import BaseModel


class ChatUser(BaseModel):
    """Represents either an authenticated or guest user."""

    user_id: str
    email: str | None = None
    role: str = "GUEST"
    is_guest: bool = True
from typing import Any
from pydantic import BaseModel, EmailStr, field_validator


class CurrentUser(BaseModel):
    user_id: int
    email: EmailStr | None = None
    role: str = "GUEST"
    is_guest: bool = False
    jwt_token: str | None = None

    @field_validator("user_id", mode="before")
    @classmethod
    def coerce_user_id_to_str(cls, v: Any) -> str:
        return str(v)

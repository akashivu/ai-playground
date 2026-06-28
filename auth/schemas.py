from pydantic import BaseModel, EmailStr


class CurrentUser(BaseModel):
    user_id: str
    email: EmailStr | None = None
    role: str = "GUEST"
    is_guest: bool = False
    jwt_token: str | None = None
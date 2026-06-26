import os

from jose import JWTError
from jose import jwt

from dotenv import load_dotenv

from auth.schemas import CurrentUser

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class AuthenticationError(Exception):
    """Raised when JWT validation fails."""


def decode_token(token: str) -> CurrentUser:
    """
    Validates a JWT and returns the authenticated user.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

    except JWTError as exc:
        raise AuthenticationError("Invalid token.") from exc

    user_id = payload.get("userId")
    email = payload.get("sub")
    role = payload.get("role")

    if (
        user_id is None
        or email is None
        or role is None
    ):
        raise AuthenticationError(
            "Missing required JWT claims."
        )

    return CurrentUser(
        user_id=user_id,
        email=email,
        role=role,
    )
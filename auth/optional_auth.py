import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt_handler import decode_token, AuthenticationError
from auth.schemas import CurrentUser

security = HTTPBearer(auto_error=False)


def get_current_or_guest_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser:
    """
    Returns an authenticated user when a valid JWT is supplied.
    Otherwise returns a temporary guest user.
    """

    if credentials is None:
        return CurrentUser(
            user_id=f"guest_{uuid.uuid4().hex}",
            role="GUEST",
            is_guest=True,
        )

    try:
        user = decode_token(credentials.credentials)

        return CurrentUser(
            user_id=str(user.user_id),
            email=user.email,
            role=user.role,
            is_guest=False,
        )

    except AuthenticationError:
        return CurrentUser(
            user_id=f"guest_{uuid.uuid4().hex}",
            role="GUEST",
            is_guest=True,
        )
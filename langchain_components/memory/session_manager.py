from uuid import uuid4


def create_session() -> str:
    """Creates and returns a new unique session ID."""
    return str(uuid4())
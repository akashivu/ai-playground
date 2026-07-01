import os

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "ACTIVE_DOMAIN",
]


def validate_environment() -> None:
    """Validates required environment variables are set before startup."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {missing}")

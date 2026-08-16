import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_MINUTES: int = 1
    GOOGLE_MAPS_API_KEY: str
    GOOGLE_PLACES_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
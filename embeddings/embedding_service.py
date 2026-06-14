import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")
        _client = OpenAI(api_key=api_key)
    return _client

def get_embedding(text: str) -> list[float]:
    """Returns embedding vector for the given text."""
    response = _get_client().embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding
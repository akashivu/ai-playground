import os
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0) -> ChatOpenAI:
    """Returns configured LangChain OpenAI chat model."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=api_key,
    )
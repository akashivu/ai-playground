import os
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler


class TokenUsageCallback(BaseCallbackHandler):
    """Captures token usage from LLM responses."""

    def __init__(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.model = ""

    def on_llm_end(self, response, **kwargs) -> None:
        usage = response.llm_output.get("token_usage", {})
        self.prompt_tokens = usage.get("prompt_tokens", 0)
        self.completion_tokens = usage.get("completion_tokens", 0)
        self.total_tokens = usage.get("total_tokens", 0)
        self.model = response.llm_output.get("model_name", "unknown")

    def to_dict(self) -> dict:
        """Returns captured usage as a dict for token logging."""
        return {
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


def get_llm(
    temperature: float = 0,
    callbacks: list | None = None,
) -> ChatOpenAI:
    """Returns configured OpenAI LLM with optional token tracking callbacks."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=api_key,
        callbacks=callbacks or [],
    )
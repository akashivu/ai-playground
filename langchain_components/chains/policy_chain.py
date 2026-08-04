from functools import lru_cache

from langchain_openai import ChatOpenAI

from config.settings import settings
from langchain_components.prompts.policy_prompt import POLICY_PROMPT
from langchain_core.output_parsers import StrOutputParser

@lru_cache(maxsize=1)
def get_policy_chain():
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,
    )
    return (
    POLICY_PROMPT
    | llm
    | StrOutputParser()
    )
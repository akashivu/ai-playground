from __future__ import annotations

from langchain_components.prompts.destination_recommendation_prompt import (
    destination_recommendation_prompt,
)

from config.llm_config import get_llm


destination_recommendation_chain = (
    destination_recommendation_prompt
    | get_llm(temperature=0)
)
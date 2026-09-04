from langchain_components.prompts.destination_recommendation_explanation_prompt import (
    destination_recommendation_explanation_prompt,
)

from config.llm_config import get_llm


destination_recommendation_explanation_chain = (
    destination_recommendation_explanation_prompt
    | get_llm(temperature=0)
)
from config.llm_config import get_llm

from langchain_components.prompts.itinerary_generation_prompt import (
    itinerary_generation_prompt,
)


itinerary_generation_chain = (
    itinerary_generation_prompt
    | get_llm(temperature=0.7)
)
from langchain_core.output_parsers import JsonOutputParser

from config.llm_config import get_llm

from langchain_components.prompts.traveler_preference_extraction_prompt import (
    traveler_preference_extraction_prompt,
)


traveler_preference_extraction_chain = (
    traveler_preference_extraction_prompt
    | get_llm(temperature=0)
    | JsonOutputParser()
)
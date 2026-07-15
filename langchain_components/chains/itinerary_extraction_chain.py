from langchain_core.output_parsers import JsonOutputParser

from config.llm_config import get_llm

from langchain_components.prompts.itinerary_extraction_prompt import (
    itinerary_extraction_prompt,
)


itinerary_extraction_chain = (
    itinerary_extraction_prompt
    | get_llm(temperature=0)
    | JsonOutputParser()
)
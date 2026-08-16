from langchain_core.output_parsers import PydanticOutputParser

from config.llm_config import get_llm

from models.generated_itinerary import (
    GeneratedItinerary,
)

from langchain_components.prompts.itinerary_generation_prompt import (
    itinerary_generation_prompt,
)


itinerary_generation_parser = (
    PydanticOutputParser(
        pydantic_object=GeneratedItinerary
    )
)


itinerary_generation_chain = (
    itinerary_generation_prompt
    | get_llm(temperature=0.7)
    | itinerary_generation_parser
)
from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser

from config.llm_config import get_llm
from models.flight_search import FlightSearchRequest
from langchain_components.prompts.flight_search_extraction_prompt import (
    flight_search_extraction_prompt,
)


flight_search_parser = PydanticOutputParser(
    pydantic_object=FlightSearchRequest
)


flight_search_extraction_chain = (
    flight_search_extraction_prompt
    | get_llm(temperature=0)
    | flight_search_parser
)
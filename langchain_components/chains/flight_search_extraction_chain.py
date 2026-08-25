from __future__ import annotations

from config.llm_config import get_llm
from models.flight_search import FlightSearchRequest
from langchain_components.prompts.flight_search_extraction_prompt import (
    flight_search_extraction_prompt,
)


flight_search_extraction_llm = get_llm(
    temperature=0
).with_structured_output(
    FlightSearchRequest
)


flight_search_extraction_chain = (
    flight_search_extraction_prompt
    | flight_search_extraction_llm
)
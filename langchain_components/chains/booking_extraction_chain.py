from langchain_core.output_parsers import JsonOutputParser
from langchain_components.prompts.booking_extraction_prompt import booking_extraction_prompt
from config.llm_config import get_llm

booking_extraction_chain = booking_extraction_prompt | get_llm(temperature=0) | JsonOutputParser()
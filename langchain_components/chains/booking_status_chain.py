from langchain_core.output_parsers import JsonOutputParser
from langchain_components.prompts.booking_status_prompt import booking_status_prompt
from config.llm_config import get_llm

booking_status_chain = booking_status_prompt | get_llm(temperature=0) | JsonOutputParser()
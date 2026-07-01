from langchain_core.output_parsers import JsonOutputParser
from langchain_components.prompts.recommendation_extraction_prompt import recommendation_extraction_prompt
from config.llm_config import get_llm

recommendation_extraction_chain = (
    recommendation_extraction_prompt | get_llm(temperature=0) | JsonOutputParser()
)

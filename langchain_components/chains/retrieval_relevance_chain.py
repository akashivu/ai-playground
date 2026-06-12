from langchain_core.output_parsers import JsonOutputParser
from config.llm_config import get_llm
from langchain_components.prompts.retrieval_relevance_prompt import retrieval_relevance_prompt

retrieval_relevance_chain = retrieval_relevance_prompt | get_llm(temperature=0) | JsonOutputParser()
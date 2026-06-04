from langchain_core.output_parsers import StrOutputParser
from config.llm_config import get_llm
from langchain_components.prompts.query_rewrite_prompt import query_rewrite_prompt

query_rewrite_chain = query_rewrite_prompt | get_llm(temperature=0) | StrOutputParser()
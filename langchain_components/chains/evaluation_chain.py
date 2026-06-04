from config.llm_config import get_llm
from langchain_components.prompts.evaluation_prompt import evaluation_prompt
from langchain_components.parsers.evaluation_parser import evaluation_parser

evaluation_chain = evaluation_prompt | get_llm(temperature=0) | evaluation_parser
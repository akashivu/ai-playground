from langchain_core.output_parsers import StrOutputParser

from config.llm_config import get_llm
from langchain_components.prompts.hallucination_prompt import hallucination_prompt

hallucination_chain = (
    hallucination_prompt
    | get_llm(temperature=0)
    | StrOutputParser()
)
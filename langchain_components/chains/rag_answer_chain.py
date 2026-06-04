from langchain_core.output_parsers import StrOutputParser
from config.llm_config import get_llm
from langchain_components.prompts.chat_rag_prompt import chat_rag_prompt

rag_answer_chain = chat_rag_prompt | get_llm(temperature=0) | StrOutputParser()
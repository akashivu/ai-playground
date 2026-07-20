from langchain_components.prompts.policy_prompt import POLICY_PROMPT
from core.dependencies import llm

policy_chain = POLICY_PROMPT | llm
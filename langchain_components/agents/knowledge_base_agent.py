from config.llm_config import get_llm
from langchain_components.tools.tool_registry import TOOLS


knowledge_base_agent = get_llm(temperature=0).bind_tools(TOOLS)
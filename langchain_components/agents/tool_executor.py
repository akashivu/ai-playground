from langchain_components.tools.tool_registry import (TOOLS,)

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS}

def execute_tool_call(tool_call,):
    """Executes a tool call returned by an LLM."""
    tool_name = (tool_call["name"])
    tool_args = (tool_call["args"])
    tool = (TOOL_MAP[tool_name])
    return tool.invoke(tool_args)
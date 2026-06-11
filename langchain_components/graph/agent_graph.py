from langgraph.graph import StateGraph, START
from langchain_components.state.conversation_state import ConversationState
from langchain_components.graph.agent_nodes.agent_node import agent_node
from langchain_components.graph.agent_nodes.tool_node import tool_node
from langchain_components.graph.agent_nodes.routing import route_agent


graph_builder = StateGraph(ConversationState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tool", tool_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", route_agent)
graph_builder.add_edge("tool", "agent")

agent_graph = graph_builder.compile()
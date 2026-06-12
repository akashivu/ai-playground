from langgraph.graph import StateGraph, START, END
from langchain_components.state.conversation_state import ConversationState
from langchain_components.graph.agentic_rag_nodes.classify_node import classify_node
from langchain_components.graph.agentic_rag_nodes.routing import route_retrieval
from langchain_components.graph.agentic_rag_nodes.relevance_node import relevance_node
from langchain_components.graph.agentic_rag_nodes.relevance_routing import route_relevance
from langchain_components.graph.nodes.retrieve_node import retrieve_node
from langchain_components.graph.nodes.answer_node import answer_node
from langchain_components.graph.agentic_rag_nodes.fallback_node import fallback_node


graph_builder = StateGraph(ConversationState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("relevance", relevance_node)
graph_builder.add_node("answer", answer_node)
graph_builder.add_node("fallback", fallback_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_conditional_edges("classify", route_retrieval)
graph_builder.add_edge("retrieve", "relevance")
graph_builder.add_conditional_edges("relevance", route_relevance)
graph_builder.add_edge("answer", END)
graph_builder.add_edge("direct_answer", END)
graph_builder.add_edge("fallback", END)

agentic_rag_graph = graph_builder.compile()
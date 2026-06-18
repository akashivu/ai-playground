from langgraph.graph import StateGraph, START, END
from langchain_components.state.conversation_state import ConversationState
from langchain_components.graph.agentic_rag_nodes.classify_node import classify_node
from langchain_components.graph.agentic_rag_nodes.routing import route_retrieval
from langchain_components.graph.agentic_rag_nodes.relevance_node import relevance_node
from langchain_components.graph.agentic_rag_nodes.relevance_retry_routing import route_relevance_or_retry
from langchain_components.graph.agentic_rag_nodes.retry_rewrite_node import retry_rewrite_node
from langchain_components.graph.nodes.retrieve_node import retrieve_node
from langchain_components.graph.nodes.answer_node import answer_node
from langchain_components.graph.agentic_rag_nodes.fallback_node import fallback_node
from langchain_components.graph.agentic_rag_nodes.retrieval_validation_routing import (
    route_after_retrieval_validation,
)


graph_builder = StateGraph(ConversationState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("relevance", relevance_node)
graph_builder.add_node("retry_rewrite", retry_rewrite_node)
graph_builder.add_node("answer", answer_node)
graph_builder.add_node("fallback", fallback_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_conditional_edges("classify", route_retrieval)
graph_builder.add_edge("retrieve", "relevance")
graph_builder.add_conditional_edges("relevance", route_relevance_or_retry)
graph_builder.add_edge("retry_rewrite", "retrieve")
graph_builder.add_edge("answer", END)
graph_builder.add_edge("fallback", END)

agentic_rag_graph = graph_builder.compile()
graph_builder.add_conditional_edges("retrieve", route_after_retrieval_validation, {
    "relevance": "relevance",
    "retry_or_fallback": "retry_rewrite",  
})
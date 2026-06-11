from langchain_components.chains.query_rewrite_chain import (query_rewrite_chain,)

def rewrite_node(state,):
    """Rewrites the user's question into a standalone query."""

    rewritten_query = (
        query_rewrite_chain.invoke(
            {
                "history": "",
                "question": state["question"],
            }
        )
    )

    return {"rewritten_query":rewritten_query}
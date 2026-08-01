from langchain_core.runnables import RunnableLambda
from langchain_components.chains.query_rewrite_chain import query_rewrite_chain
from langchain_components.chains.rag_answer_chain import rag_answer_chain
from langchain_components.runnables.hybrid_search_pipeline import hybrid_search_pipeline


def conversational_rag_workflow(data: dict) -> dict:
    question = data["question"]
    history = data.get("history", "")

    rewritten_query = query_rewrite_chain.invoke({
        "history": history,
        "question": question,
    })

    retrieved_chunks = hybrid_search_pipeline.invoke(rewritten_query)

    context = "\n\n".join(item["chunk"] for item in retrieved_chunks)

    print("\n================ RETRIEVED SOURCES ================\n")
    for item in retrieved_chunks:
        print(f"Source: {item['source']}")
        print(f"Score : {item['score']}")
        print("-" * 60)

    print("\n================ CONTEXT SENT TO LLM ================\n")
    print(context)
    print("\n=====================================================\n")

    answer = rag_answer_chain.invoke({
    "question": question,
    "context": context,
    })

    return {
        "question": question,
        "rewritten_query": rewritten_query,
        "context": context,
        "answer": answer,
    }


conversational_rag_chain = RunnableLambda(conversational_rag_workflow)
from services.retrieval_service import RetrievalService

from langchain_components.chains.query_rewrite_chain import (
    query_rewrite_chain,
)

from langchain_components.chains.rag_answer_chain import rag_answer_chain


class ConversationalRAGService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        reranking_service,
        hybrid_retrieval_service,
        evaluation_service,
    ):
        self.retrieval_service = retrieval_service
        self.reranking_service = reranking_service
        self.hybrid_retrieval_service = hybrid_retrieval_service
        self.evaluation_service = evaluation_service

    async def rewrite_query(self, messages):
        history = "\n".join(
            f"{msg.role}: {msg.content}"
            for msg in messages[:-1]
        )

        latest_question = messages[-1].content

        rewritten_query = await query_rewrite_chain.ainvoke(
            {
                "history": history,
                "question": latest_question,
            }
        )

        return rewritten_query

    async def answer_question(self, messages):
        latest_question = messages[-1].content

        rewritten_query = await self.rewrite_query(messages)

        results = self.hybrid_retrieval_service.search(rewritten_query)

        results = self.reranking_service.deduplicate(results)

        context = "\n\n".join(
            [item["chunk"] for item in results]
        )

        print("\n========== RETRIEVED RESULTS ==========")

        for i, item in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print("Source:", item["source"])
            print(item["chunk"])

        print("\n========== CONTEXT SENT TO LLM ==========")
        print(context)

        answer = await rag_answer_chain.ainvoke(
            {
                "question": latest_question,
                "context": context,
            }
        )

        evaluation = await self.evaluation_service.evaluate(
            latest_question,
            context,
            answer,
        )

        return {
            "answer": answer,
            "evaluation": evaluation,
        }
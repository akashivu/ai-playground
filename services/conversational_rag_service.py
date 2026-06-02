from services.retrieval_service import (RetrievalService,)
from services.llm_services import (generate_query_rewrite,generate_rag_response,)

class ConversationalRAGService:

    def __init__(self,retrieval_service: RetrievalService,reranking_service,):

        self.retrieval_service = (retrieval_service)
        self.reranking_service = (reranking_service)

    async def rewrite_query(self,messages):
            history = "\n".join([f"{msg.role}: {msg.content}"for msg in messages])
            prompt = f"""
                    Conversation:

                    {history}

                    Rewrite the latest user question
                    into a standalone search query.

                    Only return the rewritten query.
                    """
            
            rewritten_query = (await generate_query_rewrite(prompt))
            return rewritten_query
    

    async def answer_question(self,messages,):
         latest_question = (messages[-1].content)
         rewritten_query = (await self.rewrite_query(messages))
         results = (self.retrieval_service.search(rewritten_query))

         results = (self.reranking_service.deduplicate(results))

         results = (self.reranking_service.rerank(rewritten_query,results,))

         context = "\n\n".join([item["chunk"]for item in results])
         history = "\n".join([f"{msg.role}: {msg.content}"for msg in messages])
         prompt = f"""
                  Conversation:

                 {history}

                 Context:

                 {context}

                 Question:

                 {latest_question}

                 Use only the provided context
                 to answer the question."""
         answer = await (generate_rag_response(prompt))

         return answer
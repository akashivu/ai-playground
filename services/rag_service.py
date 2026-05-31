from services.retrieval_service import RetrievalService
from services.llm_services import generate_response

class RAGService:

    def __init__(self, retrieval_service: RetrievalService,):
        self.retrieval_service =(retrieval_service)

    def answer_question(self,question : str):
        chunks= (self.retrieval_service.search(question,top_k=3))

        context = "\n\n".join([item["chunk"]["text"]for item in chunks])
        prompt = f"""
Use ONLY the context below.

If the answer is not found,
say:

"I don't know."

Context:

{context}

Question:

{question}
"""

        response = generate_response(
            prompt
        )

        return response
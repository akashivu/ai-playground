class RerankingService:

    def rerank(self,query: str,chunks: list,top_k: int = 5,):

        query_words = (query.lower().split())

        scored_chunks = []

        for chunk in chunks:

            score = 0

            chunk_text = (chunk["chunk"].lower())

            for word in query_words:

                if word in chunk_text:

                    score += 1

            scored_chunks.append({"chunk": (chunk["chunk"]),"score": score,})

        scored_chunks.sort(key=lambda item: (item["score"]),reverse=True,)

        return scored_chunks[:top_k]
    
    def deduplicate(self,chunks: list,):

        unique_chunks = []

        seen = set()

        for chunk in chunks:

            text = (chunk["chunk"])

            if text not in seen:

                unique_chunks.append(chunk)

                seen.add(text)

        return unique_chunks
from services.retrieval_service import (RetrievalService,)

from services.bm25_service import (BM25Service,)


class HybridRetrievalService:

    def __init__(self,retrieval_service: RetrievalService,bm25_service: BM25Service,reranking_service,):

        self.retrieval_service = (retrieval_service)

        self.bm25_service = (bm25_service)

        self.reranking_service = (reranking_service)

    def search(self,query,):

        vector_results = (self.retrieval_service.search(query))

        bm25_results = (self.bm25_service.search(query))

        rrf_scores = {}
        for rank, result in enumerate(vector_results,start=1,):

               chunk = result["chunk"]
               score = ( 1 / (60 + rank))

               rrf_scores[chunk] = (rrf_scores.get(chunk,0,)+ score)

        

        for rank, result in enumerate(bm25_results,start=1,):

            chunk = result[0]

            score = (1 / (60 + rank))

            rrf_scores[chunk] = (rrf_scores.get(chunk,0,)+ score)

        sorted_results = sorted(rrf_scores.items(), key=lambda item: item[1],reverse=True,)
        reranked_results = (self.reranking_service.rerank(query,[{"chunk": item[0] }for item in sorted_results]))

        return reranked_results
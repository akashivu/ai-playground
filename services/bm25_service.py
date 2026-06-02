from rank_bm25 import BM25Okapi


class BM25Service:

    def __init__(self):

        self.documents = []

        self.bm25 = None

    def build_index(self,documents,):

        self.documents = (documents)

        tokenized_docs = [document.split()for document in documents]

        self.bm25 = (BM25Okapi(tokenized_docs))

    def search(self,query,top_k=3,):

        query_tokens = (query.split())

        scores = (self.bm25.get_scores(query_tokens))

        ranked = sorted(zip(self.documents,scores,),
            key=lambda item: (item[1]),reverse=True,)

        return ranked[:top_k]

    def add_documents(self,documents,):

       self.documents.extend(documents)

       tokenized_docs = [document.split() for document in self.documents]

       
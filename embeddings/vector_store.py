import faiss
import numpy as np
import json

class VectorStore:

    def __init__(self, dimension):

        self.index = faiss.IndexFlatL2(dimension)

        self.metadata = []

    def add_documents(self,embeddings,metadata,):

        vectors = np.array(embeddings,dtype=np.float32,)

        self.index.add(vectors)

        self.metadata.extend(metadata)

    def search(self,query_vector,k=3,collection=None,document_id=None,):

        distances, indices = self.index.search(query_vector,k,)

        results = []

        for position, idx in enumerate(indices[0]):

            metadata = self.metadata[idx]
            if (
            collection
            and metadata["collection"] != collection
        ):
                continue

            if (document_id and metadata["document_id"] != document_id):
                continue

            score = float(distances[0][position])

            results.append({"chunk": metadata["text"],
                   "source": metadata["source"],
                   "document_id": metadata["document_id"],
                   "collection": metadata["collection"],
                   "score": score,})

        return results

    def save_index(self,path,):

        faiss.write_index(self.index,path,)

    def load_index(self,path,):

        self.index = faiss.read_index(path,)

    def save_metadata(self,path,):

        with open(path,"w",encoding="utf-8",) as file:
         
         json.dump(self.metadata,file,ensure_ascii=False,indent=4,)


    def load_metadata(self,path,):

        with open(path,"r",encoding="utf-8",) as file:

         self.metadata = (json.load(file))
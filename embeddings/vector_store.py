import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension):

        self.index = faiss.IndexFlatL2(dimension)

        self.metadata = []

    def add_documents(self,embeddings,metadata,):

        vectors = np.array(embeddings,dtype=np.float32,)

        self.index.add(vectors)

        self.metadata.extend(metadata)

    def search(self,query_vector,k=3,):

        distances, indices = self.index.search(query_vector,k,)

        results = []

        for position, idx in enumerate(indices[0]):

            metadata = self.metadata[idx]

            score = float(distances[0][position])

            results.append({"chunk": metadata["text"], "source": metadata["source"], "score": score,})

        return results

    def save_index(self,path,):

        faiss.write_index(self.index,path,)

    def load_index(self,path,):

        self.index = faiss.read_index(path,)
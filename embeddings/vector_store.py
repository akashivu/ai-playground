import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension):

        self.index = faiss.IndexFlatL2(dimension)

        self.metadata = []

    def add_documents(self, embeddings, chunks):

        vectors = np.array(embeddings, dtype=np.float32)

        self.index.add(vectors)

        self.metadata.extend(chunks)

    def search(self, query_vector, k=3):

        distances, indices = self.index.search(query_vector, k)

        results = []

        for idx in indices[0]:

            results.append(self.metadata[idx])

        return results

    def save_index(self, path):

        faiss.write_index(self.index, path)

    def load_index(self, path):

        self.index = faiss.read_index(path)

from embeddings.embedding_service import get_embedding
from embeddings.sample_data import documents

import numpy as np


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


vectors = []


for doc in documents:

    vector = get_embedding(doc)

    vectors.append({"text": doc, "embedding": vector})

print("Embeddings generated")


query = "How does JWT work?"


query_vector = get_embedding(query)

scores = []


for item in vectors:

    score = cosine_similarity(query_vector, item["embedding"])

    scores.append((item["text"], score))


scores.sort(key=lambda x: x[1], reverse=True)

print("\nSearch Results:\n")

for result in scores:
    print(result)

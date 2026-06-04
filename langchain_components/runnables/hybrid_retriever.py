from langchain_core.runnables import (RunnableParallel,)
from langchain_components.runnables.vector_retriever import (vector_retriever,)
from langchain_components.runnables.bm25_retriever import (bm25_retriever,)

hybrid_retriever = RunnableParallel({"vector_results":vector_retriever,"bm25_results":bm25_retriever,})
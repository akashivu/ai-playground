from langchain_core.runnables import (RunnableLambda,)
from core.dependencies import (bm25_service,)

bm25_retriever = RunnableLambda(lambda query:bm25_service.search(query))
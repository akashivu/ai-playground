from langchain_core.runnables import (RunnableLambda,)
from core.dependencies import (retrieval_service,)

vector_retriever = RunnableLambda(lambda query:retrieval_service.search(query))
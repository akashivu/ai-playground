from langchain_core.runnables import (RunnableLambda,)
from core.dependencies import (hybrid_retrieval_service,)

hybrid_search_pipeline = RunnableLambda(lambda query:hybrid_retrieval_service.search(query))
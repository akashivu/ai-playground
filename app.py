from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.sentiment_routes import router as sentiment_router
from fastapi import Request
import time
from utils.logger import logger
from routes.search_routes import (router as search_router,)
from routes.rag_routes import (router as rag_router,)
from routes.chat_rag_routes import (router as chat_rag_router,)

app = FastAPI(title="Ai-Playground")

app.include_router(chat_router)
app.include_router(sentiment_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(chat_rag_router)

@app.get("/")
def Home():
    return {"message": "Ai backend running"}


@app.middleware("http")
async def log_request(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} took {duration:.2f}s")
    return response

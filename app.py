from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.sentiment_routes import router as sentiment_router
from fastapi import Request
import time
from utils.logger import logger
from routes.search_routes import (router as search_router,)
from routes.rag_routes import (router as rag_router,)
from routes.chat_rag_routes import (router as chat_rag_router,)
from routes.document_routes import (router as document_router,)
from routes.knowledge_base_routes import (router as knowledge_base_router,)
from routes.hybrid_search_routes import (router as hybrid_search_router,)
from routes.benchmark_routes import (router as benchmark_router,)
from routes.session_routes import router as session_router
from config.environment_validator import (validate_environment,)
from routes.health_routes import router as health_router
from contextlib import asynccontextmanager
from core.dependencies import load_vector_store
from fastapi import Request
from fastapi.responses import JSONResponse
from routes.analytics_routes import router as analytics_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.history_routes import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_environment()
    load_vector_store()
    yield

app = FastAPI(
    title="AI Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(history_router)
app.include_router(chat_router)
app.include_router(sentiment_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(chat_rag_router)
app.include_router(document_router)
app.include_router(knowledge_base_router)
app.include_router(hybrid_search_router)
app.include_router(benchmark_router)
app.include_router(session_router, prefix="/api/v1", tags=["sessions"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled exceptions and returns a safe error response."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error."},
    )

app.mount("/admin/static", StaticFiles(directory="frontend/admin"), name="admin")

@app.get("/admin")
def admin_dashboard():
    return FileResponse("frontend/admin/index.html")
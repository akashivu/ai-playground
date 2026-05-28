from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.sentiment_routes import router as sentiment_router

app = FastAPI(
    title="Ai-Playground"
)

app.include_router(chat_router)
app.include_router(sentiment_router)

@app.get("/")
def Home():
    return{
        "message":"Ai backend running"
    }

    
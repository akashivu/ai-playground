from fastapi import FastAPI
from routes.chat_routes import router

app = FastAPI(
    title="Ai-Playground"
)

app.include_router(router)

@app.get("/")
def Home():
    return{
        "message":"Ai backend running"
    }

    
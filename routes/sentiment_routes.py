from fastapi import APIRouter
from models.chat_model import ChatRequest
from services.sentiment_service import analyze_sentiment

router = APIRouter()

@router.post("/sentiment")
def sentiment(request: ChatRequest):

    try:

        last_message = request.messages[-1].content

        result = analyze_sentiment(
            last_message
        )

        return {
            "response": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }
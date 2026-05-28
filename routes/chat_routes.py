from fastapi import APIRouter
from models.chat_model import ChatRequest
from services.llm_services import generate_response

router = APIRouter()

@router.post("/chat")
def chat(request : ChatRequest):
    try:
        ai_response = generate_response(
            request.message
        )

        return{
            "response": ai_response
        }
    
    except Exception as e:
        return{
            "error": str(e)
        }

   

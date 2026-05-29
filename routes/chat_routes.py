from fastapi import APIRouter
from models.chat_model import ChatRequest
from services.llm_services import generate_response
from fastapi.responses import StreamingResponse
from services.llm_services import stream_response

router = APIRouter()

@router.post("/chat")
async def chat(request : ChatRequest):
    try:
        ai_response = await generate_response(
            request.messages
        )

        return{
            "response": ai_response
        }
    
    except Exception as e:
        return{
            "error": str(e)
        }

   
@router.post("/stream")
async def stream_chat(request : ChatRequest):
    genarator = stream_response(
        request.messages
    )

    return StreamingResponse(
        genarator,
        media_type="text/plan"
    )
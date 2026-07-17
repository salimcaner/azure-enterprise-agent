from fastapi import FastAPI, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService

app = FastAPI(title="Enterprise AI Agent")

ai_service = AIService()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/test")
def test():
    response = ai_service.generate_response("Merhaba, kendini tanit.")
    return {"response": response}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = ai_service.generate_response(request.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ChatResponse(response=response)

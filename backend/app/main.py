from fastapi import FastAPI

from app.models.chat import ChatRequest, ChatResponse
from app.services.rag.rag_service import RAGService


app = FastAPI(title="Caner Holding AI Agent")

rag_service = RAGService()


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = rag_service.ask(request.message)

    return ChatResponse(answer=answer)

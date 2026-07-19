from fastapi import FastAPI

from app.models.chat import ChatRequest, ChatResponse
from app.services.rag.rag_service import RAGService
from app.services.agent.agent_service import AgentService
from app.services.document_index_service import DocumentIndexService

app = FastAPI(title="Caner Holding AI Agent")

rag_service = RAGService()
agent_service = AgentService()
document_index_service = DocumentIndexService()


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = agent_service.chat(request.message)

    return ChatResponse(
        answer=answer,
    )

@app.post("/documents/index")
def index_document():
    indexed_documents = document_index_service.index_document(
        "data/pdf/Company_Policies.pdf"
    )

    return {
        "indexed_documents": indexed_documents,
    }

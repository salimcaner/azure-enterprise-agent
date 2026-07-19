from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router

app = FastAPI(title="Caner Holding AI Agent")

app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/")
def root():
    return {"status": "running"}

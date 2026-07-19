from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.document.document_index_service import DocumentIndexService

router = APIRouter()
document_index_service = DocumentIndexService()


@router.post("/documents")
def index_document(file: UploadFile = File(...)):
    indexed_document = document_index_service.index_upload(file)

    return {
        "document_id": indexed_document.document_id,
        "file_name": indexed_document.file_name,
        "file_type": indexed_document.file_type,
        "uploaded_at": indexed_document.uploaded_at,
        "indexed_chunks": indexed_document.indexed_chunks,
    }


@router.get("/documents")
def list_documents():
    documents = document_index_service.list_documents()
    return {
        "documents": [
            {
                "document_id": doc.document_id,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "uploaded_at": doc.uploaded_at,
            }
            for doc in documents
        ],
    }


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    try:
        file_name = document_index_service.delete_document(document_id)
        return {
            "deleted_document_id": document_id,
            "file_name": file_name,
            "status": "success",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


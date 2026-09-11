from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from ..rag.pipeline import RAGPipeline
from ..config import get_settings, Settings

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000, examples=["How do I roll back a failed deployment?"])


class Citation(BaseModel):
    document_id: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    chunk_id: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    retrieved_chunks: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    vector_store_chunks: int
    llm_configured: bool


# Dependency injection of the pipeline (set on app startup)
_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    return _pipeline


def set_pipeline(pipeline: RAGPipeline) -> None:
    global _pipeline
    _pipeline = pipeline


@router.get("/health", response_model=HealthResponse)
def health(pipeline: RAGPipeline = Depends(get_pipeline)):
    return HealthResponse(
        status="ok",
        vector_store_chunks=pipeline.vector_store.collection.count(),
        llm_configured=pipeline.llm_client is not None,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, pipeline: RAGPipeline = Depends(get_pipeline)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = pipeline.chat(request.question.strip())
    return ChatResponse(
        answer=result["answer"],
        citations=[Citation(**c) for c in result.get("citations", [])],
        retrieved_chunks=result.get("retrieved_chunks", 0),
        error=result.get("error"),
    )


@router.post("/reindex")
def reindex(pipeline: RAGPipeline = Depends(get_pipeline)):
    """Force re-ingestion of all documents (useful after updating knowledge base files)."""
    result = pipeline.ingest_documents(force_reindex=True)
    return result

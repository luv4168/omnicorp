import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .rag.pipeline import RAGPipeline
from .api import chat as chat_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("omnicorp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting OmniCorp RAG Chatbot backend...")

    pipeline = RAGPipeline(settings)
    chat_api.set_pipeline(pipeline)

    # Ingest documents on startup
    try:
        result = pipeline.ingest_documents()
        logger.info(f"Ingestion result: {result}")
    except Exception as e:
        logger.exception("Failed to ingest documents on startup")
        # We still start the server so the health endpoint can report the issue

    yield

    logger.info("Shutting down...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="OmniCorp RAG Chatbot API",
        description="Retrieval-Augmented Generation chatbot for Customer Success Managers",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins + ["*"],  # permissive for local demo
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_api.router)

    @app.get("/")
    def root():
        return {
            "service": "OmniCorp RAG Chatbot",
            "docs": "/docs",
            "health": "/api/health",
            "chat": "POST /api/chat",
        }

    return app


app = create_app()

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # LLM provider settings (OpenAI-compatible)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"  # change for Groq / Ollama
    openai_model: str = "gpt-4o-mini"

    # Embeddings – we use a local sentence-transformers model by default
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Paths
    documents_path: str = "documents"
    chroma_persist_dir: str = "data/chroma"

    # RAG parameters
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://frontend:80"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

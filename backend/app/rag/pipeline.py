from typing import List, Optional
from openai import OpenAI
from .documents import load_and_chunk_documents, DocumentChunk
from .vectorstore import VectorStore
from ..config import Settings
import logging

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert Customer Success assistant for OmniCorp Solutions.
You answer questions from Customer Success Managers strictly based on the provided internal documentation excerpts.

Rules:
- Use ONLY the information present in the context below. Do not invent features, procedures, or policies.
- If the context does not contain enough information to answer confidently, say so clearly and suggest which document the user should consult.
- Always be precise and professional.
- When you reference information, mention the document title or Document ID when possible.
- Keep answers concise but complete enough for a CSM to act on.
"""


class RAGPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.vector_store = VectorStore(
            persist_directory=settings.chroma_persist_dir,
            embedding_model_name=settings.embedding_model,
        )
        self.llm_client: Optional[OpenAI] = None
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        if not self.settings.openai_api_key:
            logger.warning(
                "OPENAI_API_KEY is not set. The /chat endpoint will return a helpful error "
                "until a key (or Ollama/Groq endpoint) is configured."
            )
            return

        self.llm_client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )
        logger.info(f"LLM client initialized → {self.settings.openai_base_url} / {self.settings.openai_model}")

    def ingest_documents(self, force_reindex: bool = False) -> dict:
        """Load, chunk and index all markdown documents."""
        if not force_reindex and not self.vector_store.is_empty():
            count = self.vector_store.collection.count()
            logger.info(f"Vector store already contains {count} chunks – skipping ingestion.")
            return {"status": "skipped", "chunks": count}

        logger.info("Starting document ingestion...")
        chunks = load_and_chunk_documents(
            documents_path=self.settings.documents_path,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.vector_store.add_chunks(chunks)
        return {"status": "indexed", "chunks": len(chunks), "sources": list({c.source for c in chunks})}

    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[dict]:
        k = top_k or self.settings.top_k
        return self.vector_store.query(question, top_k=k)

    def generate_answer(self, question: str, retrieved: List[dict]) -> dict:
        if not self.llm_client:
            return {
                "answer": (
                    "The language model is not configured. "
                    "Please set OPENAI_API_KEY (and optionally OPENAI_BASE_URL / OPENAI_MODEL) "
                    "in the environment or .env file. "
                    "You can use OpenAI, Groq, or a local Ollama instance."
                ),
                "citations": [],
                "error": "llm_not_configured",
            }

        if not retrieved:
            return {
                "answer": "I could not find any relevant information in the internal knowledge base for this question.",
                "citations": [],
            }

        # Build context with clear source markers
        context_parts = []
        citations = []
        seen_sources = set()

        for i, hit in enumerate(retrieved, start=1):
            meta = hit["metadata"]
            source_label = f"[{i}] {meta.get('title', meta.get('source'))} ({meta.get('document_id', 'N/A')})"
            context_parts.append(f"{source_label}\n{hit['content']}")

            key = (meta.get("document_id"), meta.get("source"))
            if key not in seen_sources:
                seen_sources.add(key)
                citations.append(
                    {
                        "document_id": meta.get("document_id"),
                        "title": meta.get("title"),
                        "source": meta.get("source"),
                        "chunk_id": hit["id"],
                        "relevance_score": round(1 - hit["distance"], 4),  # cosine distance → similarity-ish
                    }
                )

        context = "\n\n---\n\n".join(context_parts)

        user_message = f"""Context from internal OmniCorp documentation:

{context}

---

Question from CSM: {question}

Provide a clear, accurate answer based only on the context above. If the context is insufficient, say so."""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            logger.exception("LLM call failed")
            return {
                "answer": f"Sorry, I encountered an error while generating the answer: {str(e)}",
                "citations": citations,
                "error": "llm_error",
            }

        return {
            "answer": answer,
            "citations": citations,
        }

    def chat(self, question: str) -> dict:
        retrieved = self.retrieve(question)
        result = self.generate_answer(question, retrieved)
        result["retrieved_chunks"] = len(retrieved)
        return result

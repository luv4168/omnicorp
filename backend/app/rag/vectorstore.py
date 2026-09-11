from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from .documents import DocumentChunk
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(
        self,
        persist_directory: str,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name: str = "omnicorp_kb",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedder = SentenceTransformer(embedding_model_name)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def is_empty(self) -> bool:
        return self.collection.count() == 0

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        if not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "source": c.source,
                "title": c.title,
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ]

        logger.info(f"Embedding {len(chunks)} chunks...")
        embeddings = self.embedder.encode(documents, show_progress_bar=False).tolist()

        # Chroma has a limit on batch size; add in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {self.collection.count()}")

    def query(self, query_text: str, top_k: int = 4) -> List[dict]:
        query_embedding = self.embedder.encode([query_text]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                hits.append(
                    {
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )
        return hits

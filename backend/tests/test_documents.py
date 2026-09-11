import pytest
from pathlib import Path
from app.rag.documents import load_and_chunk_documents


def test_load_and_chunk_documents():
    docs_path = Path(__file__).parent.parent / "documents"
    chunks = load_and_chunk_documents(str(docs_path), chunk_size=600, chunk_overlap=100)

    assert len(chunks) > 5, "Expected multiple chunks from the knowledge base"
    assert all(c.content.strip() for c in chunks)
    assert all(c.source.endswith(".md") for c in chunks)
    assert any("KB-001" in c.document_id for c in chunks)
    assert any("Platform" in c.title or "Overview" in c.title for c in chunks)


def test_chunks_have_unique_ids():
    docs_path = Path(__file__).parent.parent / "documents"
    chunks = load_and_chunk_documents(str(docs_path))
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs must be unique"

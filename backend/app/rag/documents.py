from pathlib import Path
from dataclasses import dataclass
from typing import List
import re


@dataclass
class DocumentChunk:
    id: str
    content: str
    source: str          # filename
    title: str           # extracted from first heading
    document_id: str     # e.g. KB-001
    chunk_index: int


def _extract_title_and_id(text: str, filename: str) -> tuple[str, str]:
    """Extract title (first H1) and Document ID if present."""
    title = filename.replace(".md", "").replace("_", " ").title()
    doc_id = "UNKNOWN"

    lines = text.splitlines()
    for line in lines[:15]:
        if line.startswith("# "):
            title = line[2:].strip()
        match = re.search(r"Document ID:\s*([A-Z0-9-]+)", line, re.IGNORECASE)
        if match:
            doc_id = match.group(1)
    return title, doc_id


def load_and_chunk_documents(
    documents_path: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[DocumentChunk]:
    """
    Load all .md files from the given directory and split them into overlapping chunks.
    Simple character-based chunking that respects paragraph boundaries when possible.
    """
    path = Path(documents_path)
    if not path.exists():
        raise FileNotFoundError(f"Documents directory not found: {documents_path}")

    chunks: List[DocumentChunk] = []
    md_files = sorted(path.glob("*.md"))

    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {documents_path}")

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")
        title, doc_id = _extract_title_and_id(text, file_path.name)

        # Simple recursive-ish splitting by paragraphs first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        current_chunk = ""
        chunk_idx = 0

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = (current_chunk + "\n\n" + para).strip()
            else:
                if current_chunk:
                    chunks.append(
                        DocumentChunk(
                            id=f"{file_path.stem}-{chunk_idx}",
                            content=current_chunk,
                            source=file_path.name,
                            title=title,
                            document_id=doc_id,
                            chunk_index=chunk_idx,
                        )
                    )
                    chunk_idx += 1
                    # overlap: keep the end of previous chunk
                    overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                    current_chunk = (overlap_text + "\n\n" + para).strip()
                else:
                    # single paragraph longer than chunk_size → hard split
                    for i in range(0, len(para), chunk_size - chunk_overlap):
                        piece = para[i : i + chunk_size]
                        chunks.append(
                            DocumentChunk(
                                id=f"{file_path.stem}-{chunk_idx}",
                                content=piece,
                                source=file_path.name,
                                title=title,
                                document_id=doc_id,
                                chunk_index=chunk_idx,
                            )
                        )
                        chunk_idx += 1
                    current_chunk = ""

        if current_chunk:
            chunks.append(
                DocumentChunk(
                    id=f"{file_path.stem}-{chunk_idx}",
                    content=current_chunk,
                    source=file_path.name,
                    title=title,
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                )
            )

    return chunks

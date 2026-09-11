# OmniCorp RAG Chatbot – Customer Success Knowledge Assistant

Prototype **Retrieval-Augmented Generation (RAG)** chatbot that lets Customer Success Managers ask natural-language questions about OmniCorp’s internal product documentation and receive accurate, **cited** answers.

---

## Tools & AI Assistance

This prototype was developed with AI pair-programming assistance (Grok / xAI).

| Component | Tools / Libraries used |
|-----------|------------------------|
| **Backend** | Python, FastAPI, ChromaDB, sentence-transformers, openai (OpenAI-compatible client) |
| **Frontend** | React, Vite, TypeScript (custom CSS; Tailwind was optional and not required) |
| **RAG** | Raw SDKs (no LangChain / LlamaIndex / Semantic Kernel) – transparent retrieve-then-generate loop |
| **LLM** | OpenAI-compatible (works with OpenAI, Groq, Ollama, etc. via BYOK) |
| **Orchestration** | Docker Compose |
| **Testing** | pytest |

A full reconstruction of the development conversation, key prompts, and tool rationale is available in:

**[`AI_CONVERSATION_LOG.md`](./AI_CONVERSATION_LOG.md)**

---

## Architecture Overview

```
┌─────────────────┐       ┌──────────────────────────────────────────┐
│  React (Vite)   │──────▶│  FastAPI Backend                         │
│  Chat UI        │  HTTP │                                          │
│  + Citations    │◀──────│  • Document ingestion & chunking         │
└─────────────────┘       │  • Local embeddings (sentence-transformers)│
                          │  • ChromaDB vector store (persistent)     │
                          │  • OpenAI-compatible LLM (OpenAI/Groq/   │
                          │    Ollama) for answer generation         │
                          └──────────────────────────────────────────┘
```

### Design Decisions & Trade-offs

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend language | Python + FastAPI | Best ecosystem for RAG (Chroma, sentence-transformers, OpenAI client). Fast to prototype, excellent DX. |
| Embeddings | Local `all-MiniLM-L6-v2` | No extra API cost or key required for retrieval. Good quality for technical documentation. Model is downloaded once at image build time. |
| Vector store | ChromaDB (persistent) | Simple, pure-Python, runs entirely locally, supports metadata filtering. Sufficient for a prototype; can be swapped for Qdrant/Weaviate later. |
| LLM | OpenAI-compatible client | One code path works with OpenAI, Groq, Azure OpenAI, or local Ollama. Reviewer supplies their own key. |
| Chunking | Paragraph-aware + overlap | Preserves semantic units better than naive fixed-size splits while staying simple (no LangChain dependency). |
| Frontend | React + Vite + TypeScript | Lightweight, modern, easy to extend. Citations rendered clearly under every answer. |
| Orchestration | Docker Compose | One command brings up the full stack. Health-checks ensure the frontend only starts after the backend is ready. |

**What was deliberately kept simple (prototype scope):**
- No authentication / multi-tenancy
- No conversation memory (stateless per request)
- No streaming responses
- No advanced re-ranking or hybrid search
- Basic character/paragraph chunking instead of a full document AI pipeline

These can be added incrementally without changing the core architecture.

---

## Knowledge Base

Five realistic mock articles are included under `backend/documents/`:

| File | Document ID | Topic |
|------|-------------|-------|
| `01_platform_overview.md` | KB-001 | Product overview, components, licensing |
| `02_configuration_packages.md` | KB-002 | Packages, versioning, promotion |
| `03_policy_engine.md` | KB-003 | Policies, evaluation points, common failures |
| `04_deployment_and_rollback.md` | KB-004 | Strategies, monitoring, rollback |
| `05_troubleshooting_common_issues.md` | KB-005 | Auth, drift, quotas, timeouts |

---

## Quick Start (Docker – recommended)

### 1. Prerequisites
- Docker + Docker Compose
- An API key for an OpenAI-compatible provider **or** a running Ollama instance

### 2. Configure the LLM

Copy the example env file and edit it:

```bash
cp backend/.env.example .env
```

**Option A – OpenAI**
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**Option B – Groq (fast & free tier)**
```env
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
```

**Option C – Local Ollama**
```env
OPENAI_API_KEY=ollama          # any non-empty value
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_MODEL=llama3.2
```
(Make sure Ollama is running on the host and the model is pulled.)

### 3. Launch

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/health

The first build downloads the embedding model and may take a few minutes. Subsequent starts are much faster thanks to the persistent Chroma volume.

---

## Local Development (without Docker)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit with your key
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server proxies `/api` to `localhost:8000`.

---

## API Design

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health + vector-store size + whether LLM is configured |
| `POST` | `/api/chat` | Main RAG endpoint |
| `POST` | `/api/reindex` | Force re-ingestion of all documents |

### Chat Request
```json
{
  "question": "How do I roll back a failed deployment?"
}
```

### Chat Response
```json
{
  "answer": "To perform a manual rollback…",
  "citations": [
    {
      "document_id": "KB-004",
      "title": "Deployment Orchestrator & Rollback Procedures",
      "source": "04_deployment_and_rollback.md",
      "chunk_id": "04_deployment_and_rollback-2",
      "relevance_score": 0.87
    }
  ],
  "retrieved_chunks": 4
}
```

---

## Testing

```bash
cd backend
pytest tests/ -v
```

Currently covers document loading & chunking. Additional integration tests can be added against a running instance.

---

## Project Structure

```
omnicorp-rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + lifespan
│   │   ├── config.py            # Settings from env
│   │   ├── api/chat.py          # /api/chat, /health, /reindex
│   │   └── rag/
│   │       ├── documents.py     # Load + chunk markdown
│   │       ├── vectorstore.py   # Chroma + sentence-transformers
│   │       └── pipeline.py      # Retrieve → generate
│   ├── documents/               # Knowledge-base articles
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/Chat.tsx  # Chat UI + citation rendering
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Operational Notes

- **Embeddings** are computed once at startup (or on `/reindex`). The Chroma volume persists across container restarts.
- **No secrets** are baked into the image. The reviewer supplies `OPENAI_API_KEY` (and optional base URL / model) via environment variables or a `.env` file.
- The frontend never sees the API key; all LLM calls happen server-side.
- CORS is intentionally permissive for local demos.

---

## Future Improvements (out of scope for this prototype)

- Conversation history / multi-turn context
- Streaming answers (SSE)
- Hybrid search (BM25 + vector)
- Role-based access and document-level permissions
- Evaluation harness (RAGAS / custom golden set)
- Observability (OpenTelemetry traces for retrieval + generation latency)

---

Built as a focused engineering prototype demonstrating clean architecture, API design, and operational readiness for a Customer Success RAG assistant.

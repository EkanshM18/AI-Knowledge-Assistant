# AI Knowledge Assistant

A production-style, resume-ready AI Knowledge Assistant built with FastAPI, React, LlamaIndex, Qdrant, LangGraph, and a Supabase-backed cloud upload pipeline.

## What This Project Demonstrates

- Enterprise document ingestion across PDF, TXT, DOCX, Markdown, CSV, JSON, and HTML
- Supabase Storage for uploaded files
- PostgreSQL metadata storage in Supabase
- Async ingestion from Supabase objects into Qdrant
- Free Hugging Face embeddings with `BAAI/bge-small-en-v1.5`
- Grounded RAG answers with citations
- Memory-aware conversations
- Multi-agent orchestration with LangGraph
- FastAPI backend and React + Tailwind frontend

## Architecture

### Backend

- `FastAPI` for APIs and application lifecycle
- `Supabase Storage` for uploaded document objects
- `Supabase Postgres` for document metadata and ingestion status
- `LlamaIndex` ingestion pipeline for chunking and embeddings
- `Qdrant` local mode for vector persistence
- `Transformers` for local answer generation
- `LangGraph` for router, retriever, synthesizer, validator, and memory flow

### Frontend

- `React` for UI
- `TailwindCSS` for styling
- Drag-and-drop enterprise upload experience
- Upload progress and live ingestion status tracking

## Project Structure

```text
ai-knowledge-assistant/
├── app/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── ingestion/
│   ├── models/
│   ├── services/
│   ├── vectorstore/
│   └── main.py
├── frontend/
├── qdrant_data/
├── supabase/
│   └── migrations/
├── .env.example
├── README.md
└── requirements.txt
```

## Step-By-Step Build Plan

### Phase 1: Foundation

1. Create a modular FastAPI backend.
2. Configure cloud storage, vector, and runtime settings.
3. Add upload, document listing, and chat APIs.
4. Scaffold the React + Tailwind frontend.

### Phase 2: Cloud Ingestion Pipeline

1. Upload files directly to Supabase Storage.
2. Persist document metadata in Supabase Postgres.
3. Download uploaded files from Supabase for ingestion.
4. Convert raw bytes into `LlamaIndex` `Document` objects.
5. Chunk documents with `SentenceSplitter`.
6. Generate embeddings with `HuggingFaceEmbedding`.
7. Upsert chunk vectors plus metadata into Qdrant.
8. Update ingestion status in PostgreSQL.

### Phase 3: Multi-Agent Workflow

1. `Memory Agent` prepares recent conversation context.
2. `Router Agent` decides whether retrieval is needed.
3. `Retriever Agent` pulls relevant chunks from Qdrant.
4. `Response Synthesizer Agent` drafts the grounded answer.
5. `Validator Agent` checks whether the answer is sufficiently grounded.

### Phase 4: Frontend Experience

1. Add drag-and-drop document upload flow.
2. Add upload progress feedback.
3. Show document ingestion status from PostgreSQL.
4. Add enterprise-style chat UI.
5. Display source citations and retrieval evidence.
6. Handle loading, errors, and empty states cleanly.

### Phase 5: Production Hardening

1. Add structured logging.
2. Add persistent chat storage.
3. Add reranking and hybrid retrieval.
4. Add authentication and role-based access.
5. Add tests, monitoring, and deployment packaging.

## Local Setup

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Supabase Setup

1. Create a Supabase project.
2. Create a storage bucket named `enterprise-documents`.
3. Apply the SQL migration in `supabase/migrations/0001_documents.sql`.
4. Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_CONNECTION_STRING` in `.env`.
5. Set `SUPABASE_STORAGE_BUCKET=enterprise-documents` and `SUPABASE_DOCUMENTS_TABLE=documents`.

## API Endpoints

- `GET /api/health`
- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/stats`
- `POST /api/chat`

## Environment Variables

Backend:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `SUPABASE_CONNECTION_STRING`
- `SUPABASE_STORAGE_BUCKET`
- `SUPABASE_DOCUMENTS_TABLE`
- `QDRANT_COLLECTION`
- `PIPELINE_CACHE_DIR`

Frontend:

- `VITE_API_BASE_URL`

## Default Models

- Embeddings: `BAAI/bge-small-en-v1.5`
- LLM: `google/flan-t5-base`

You can swap models in `.env` without changing the core pipeline.

## Notes

- Uploaded files are stored in Supabase Storage, not on the local filesystem.
- Document metadata and ingestion state are stored in Supabase Postgres.
- The ingestion pipeline downloads the object from Supabase, processes it, and upserts embeddings to Qdrant.
- The validator is intentionally conservative and prefers declining unsupported claims over hallucinating.

## Useful References

- LlamaIndex ingestion pipeline: https://docs.llamaindex.ai/en/stable/module_guides/loading/ingestion_pipeline/
- LlamaIndex Hugging Face embeddings: https://docs.llamaindex.ai/en/stable/examples/embeddings/huggingface/
- Qdrant local client docs: https://python-client.qdrant.tech/qdrant_client.local.qdrant_local
- LangGraph graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Supabase docs: https://supabase.com/docs

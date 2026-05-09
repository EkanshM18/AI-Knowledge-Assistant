# AI Knowledge Assistant

A production-style, resume-ready AI Knowledge Assistant built with local open-source models, modular RAG architecture, and LangGraph-based multi-agent orchestration.

## What This Project Demonstrates

- Enterprise document ingestion across PDF, TXT, DOCX, Markdown, CSV, JSON, and HTML
- Local embeddings with `BAAI/bge-small-en-v1.5`
- Local vector search with `QdrantClient(path="qdrant_data")`
- Local answer generation with replaceable Hugging Face models
- Grounded RAG answers with citations
- Memory-aware conversations
- Multi-agent orchestration with LangGraph
- FastAPI backend and React + Tailwind frontend

## Architecture

### Backend

- `FastAPI` for APIs and application lifecycle
- `LlamaIndex` ingestion pipeline for chunking and embeddings
- `Qdrant` local mode for vector persistence
- `Transformers` for local answer generation
- `LangGraph` for router, retriever, synthesizer, validator, and memory flow

### Frontend

- `React` for UI
- `TailwindCSS` for styling
- Source-aware chat experience with upload and retrieval feedback

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
├── data/
├── frontend/
├── qdrant_data/
├── .env.example
├── README.md
└── requirements.txt
```

## Step-By-Step Build Plan

### Phase 1: Foundation

1. Create a modular FastAPI backend.
2. Configure local-only model, storage, and runtime settings.
3. Add upload and chat APIs.
4. Scaffold the React + Tailwind frontend.

### Phase 2: RAG Pipeline

1. Load uploaded files and normalize text.
2. Convert raw text into `LlamaIndex` `Document` objects.
3. Chunk documents with `SentenceSplitter`.
4. Generate embeddings with `HuggingFaceEmbedding`.
5. Upsert chunk vectors plus metadata into local Qdrant.
6. Embed user questions and retrieve top-k relevant chunks.
7. Generate grounded answers from retrieved context only.

### Phase 3: Multi-Agent Workflow

1. `Memory Agent` prepares recent conversation context.
2. `Router Agent` decides whether retrieval is needed.
3. `Retriever Agent` pulls relevant chunks from Qdrant.
4. `Response Synthesizer Agent` drafts the grounded answer.
5. `Validator Agent` checks whether the answer is sufficiently grounded.

### Phase 4: Frontend Experience

1. Add document upload flow.
2. Add enterprise-style chat UI.
3. Display source citations and retrieval evidence.
4. Handle loading, errors, and empty states cleanly.

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

## API Endpoints

- `GET /api/health`
- `POST /api/documents/upload`
- `GET /api/documents/stats`
- `POST /api/chat`

## Default Local Models

- Embeddings: `BAAI/bge-small-en-v1.5`
- LLM: `google/flan-t5-base`

You can swap models in `.env` without changing the core pipeline.

## Notes

- The validator is intentionally conservative and prefers declining unsupported claims over hallucinating.
- The current memory store is in-memory to keep local setup simple.
- Qdrant local mode is ideal for local development and portfolio demos.

## Useful References

- LlamaIndex ingestion pipeline: https://docs.llamaindex.ai/en/stable/module_guides/loading/ingestion_pipeline/
- LlamaIndex Hugging Face embeddings: https://docs.llamaindex.ai/en/stable/examples/embeddings/huggingface/
- Qdrant local client docs: https://python-client.qdrant.tech/qdrant_client.local.qdrant_local
- LangGraph graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api

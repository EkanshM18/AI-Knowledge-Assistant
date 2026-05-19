# Implementation Guide

This document turns the project into a practical execution plan you can follow, present, and extend.

## Step 1: Prepare the Backend Runtime

1. Create and activate a virtual environment.
2. Install `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Add `SUPABASE_SERVICE_ROLE_KEY` and `SUPABASE_CONNECTION_STRING`.
5. Start the FastAPI server with `uvicorn app.main:app --reload`.

Expected outcome:

- FastAPI starts locally on `http://127.0.0.1:8000`
- Qdrant local storage is created under `qdrant_data/`
- Supabase client configuration loads successfully
- Upload, document listing, stats, and chat endpoints are available

## Step 2: Prepare the Frontend Runtime

1. Move into `frontend/`.
2. Install packages with `npm install`.
3. Copy `frontend/.env.example` if you want a custom backend URL.
4. Run `npm run dev`.

Expected outcome:

- React app starts on `http://127.0.0.1:5173`
- Frontend can call backend health, upload, document list, stats, and chat APIs

## Step 3: Ingest Enterprise Documents

Flow:

1. Upload one or more files from the UI.
2. Backend streams file bytes directly to `enterprise-documents` bucket in Supabase.
3. Backend writes a metadata row into Supabase Postgres.
4. `IngestionService` retrieves the file bytes from Supabase Storage.
5. `DocumentLoader` (using `BytesIO`) extracts normalized text from in-memory bytes.
6. `SentenceSplitter` creates semantic chunks.
7. `HuggingFaceEmbedding` generates embeddings.
8. `QdrantService` upserts chunk vectors and metadata into local Qdrant.
9. Backend updates ingestion status in PostgreSQL.

Metadata persisted per document:

- `id`
- `filename`
- `storage_path`
- `file_type`
- `upload_timestamp`
- `ingestion_status`
- `vector_collection`
- `vector_count`
- `chunk_count`
- `file_size`
- `mime_type`
- `tags`
- `metadata`

## Step 4: Run a Grounded Query

Flow:

1. Frontend sends a chat message to `POST /api/chat`.
2. `MemoryService` resolves session history.
3. `Router Agent` decides between memory-only and retrieval-backed response.
4. `Retriever Agent` embeds the question and searches Qdrant.
5. `Response Synthesizer Agent` prompts the local Hugging Face model using retrieved chunks only.
6. `Validator Agent` checks whether the answer is sufficiently grounded in the retrieved evidence.
7. API returns the answer plus source citations.

## Step 5: Explain the LangGraph Agent Design

Current graph:

- `memory`
- `router`
- `retriever`
- `synthesizer`
- `validator`

Routing behavior:

- Memory route: used for conversation-history questions
- Retrieval route: used for normal enterprise knowledge questions
- Summarization route: currently routed through retrieval so summaries remain grounded in documents

## Step 6: Portfolio Talking Points

Use these points in your resume or interview walkthrough:

- Built a modular enterprise RAG platform with Supabase-backed cloud storage and metadata persistence
- Implemented LlamaIndex ingestion for chunking and embeddings
- Used Qdrant local persistent storage without Docker
- Orchestrated multi-agent workflows using LangGraph
- Added an ingestion status pipeline to reduce user uncertainty during uploads
- Delivered FastAPI backend plus React/Tailwind frontend
- Designed the system for model swap flexibility and future hybrid retrieval

## Step 7: Recommended Next Enhancements

### Retrieval Quality

1. Add BM25 sparse retrieval.
2. Add reciprocal rank fusion.
3. Add reranking with a local cross-encoder.

### Enterprise Readiness

1. Persist chat history in SQLite or PostgreSQL.
2. Add authentication and document-level access control.
3. Add audit logging and request tracing.

### Multi-Agent Depth

1. Add an explicit policy agent for compliance-heavy queries.
2. Add a planner agent for multi-hop enterprise tasks.
3. Add tool-calling nodes for structured database or API lookup.

### Evaluation

1. Add benchmark question sets.
2. Track retrieval hit rate and grounding rate.
3. Create regression tests for ingestion and chat workflows.

## Step 8: Suggested Demo Script

1. Launch backend and frontend.
2. Show health and vector stats at zero.
3. Upload sample enterprise documents.
4. Watch the upload progress and ingestion status updates.
5. Ask a factual question from one uploaded document.
6. Show the cited sources panel.
7. Ask a follow-up question in the same session.
8. Explain the router, retriever, synthesizer, and validator flow.

## Step 9: Model Swap Options

You can switch the LLM in `.env`:

- `google/flan-t5-base` for light local usage
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` for small chat-style generation
- `mistralai/Mistral-7B-Instruct-v0.2` for stronger reasoning on capable hardware

You can switch embeddings in `.env`:

- `BAAI/bge-small-en-v1.5`
- `intfloat/e5-small-v2`
- `sentence-transformers/all-MiniLM-L6-v2`

## Step 10: What To Build Next If You Want This To Feel More Enterprise

1. Add user authentication.
2. Add department-level metadata filters.
3. Add conversation persistence and replay.
4. Add ingestion queues and background jobs.
5. Add dashboards for indexing volume, latency, and grounding quality.

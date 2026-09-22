# Personal Knowledge Agent (Jarvis Lite)

A personal document assistant built step by step as an Applied AI portfolio project.

## Goal

Upload PDF, Markdown, and text documents; ask questions about them; and receive answers with verifiable source references. The first release will use React, FastAPI, PostgreSQL, and `pgvector`.

## Current status

The project scope is documented in [docs/MVP.md](docs/MVP.md). The first working component is a small FastAPI service with a health endpoint. Document ingestion, retrieval, and chat are planned next; they are not implemented yet.

## Run the API locally

Requirements: Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn jarvis.main:app --reload
```

Open <http://127.0.0.1:8000/health> to check the service. Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

## Planned milestones

1. Document upload and text extraction.
2. Chunking, embeddings, and retrieval with PostgreSQL and `pgvector`.
3. Question answering with source references and conversation history.
4. A bounded agent loop with document search, calculator, and read-only finance access.
5. Evaluation, safety checks, observability, Docker, CI, and deployment.

Each milestone will be implemented and verified in small increments.

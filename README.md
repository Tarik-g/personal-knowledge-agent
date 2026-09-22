# Personal Knowledge Agent (Jarvis Lite)

A personal document assistant built step by step as an Applied AI portfolio project.

## Goal

Upload a PDF, ask a question about it, and receive an answer with a verifiable page reference and supporting excerpt. The first release will use React, FastAPI, PostgreSQL, and `pgvector`.

## Current status

The exact first-release scope and acceptance criteria are documented in [docs/MVP.md](docs/MVP.md). The first working component is a small FastAPI service with a health endpoint. PDF ingestion, retrieval, and question answering are planned next; they are not implemented yet.

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

1. PDF upload, validation, and page-aware text extraction.
2. Chunking, embeddings, and retrieval with PostgreSQL and `pgvector`.
3. Question answering with page references, supporting excerpts, and a small React interface.
4. A bounded agent loop with tools and error handling.
5. Evaluation, safety checks, observability, Docker, CI, and deployment.

Each milestone will be implemented and verified in small increments.

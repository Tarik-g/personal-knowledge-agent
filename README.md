# Personal Knowledge Agent (Jarvis Lite)

A personal document assistant built step by step as an Applied AI portfolio project.

## Goal

Upload a PDF, ask a question about it, and receive an answer with a verifiable page reference and supporting excerpt. The first release will use React, FastAPI, PostgreSQL, and `pgvector`.

## Current status

The exact first-release scope and acceptance criteria are documented in [docs/MVP.md](docs/MVP.md). The API has a health endpoint and a `POST /documents/extract` endpoint for text-based PDFs up to 10 MiB. It returns page text and smaller, page-aware passages. Retrieval and question answering are planned next; they are not implemented yet.

## Run the API locally

From the repository root, start the API with one command:

```powershell
python -m uvicorn jarvis.main:app --reload
```

For a fresh Python installation, install the project dependencies once with `python -m pip install --user -e .`. Python 3.11 or newer is required.

Open <http://127.0.0.1:8000/> for the interactive API documentation, or <http://127.0.0.1:8000/health> to check the service.

To inspect a local text-based PDF from Python:

```python
from jarvis.pdf import extract_pages
from jarvis.chunking import chunk_pages

pages = extract_pages("path/to/document.pdf")
chunks = chunk_pages(pages)
print(chunks)
```

## Vector search without Docker

This project uses hosted PostgreSQL with `pgvector`, so local development and the eventual online demo can connect to the same kind of database. For the first database exercise, create a PostgreSQL project on [Neon](https://neon.com/) and paste the contents of [db/vector_demo.sql](db/vector_demo.sql) into its SQL Editor. Run the whole script together: it creates a temporary example table and lists the closest vectors first.

The three-number vectors in that script are made-up examples, not embeddings calculated from the labels. A real document table and a `DATABASE_URL` connection will follow when we implement retrieval. Keep the connection string in an environment variable, never in Git.

For the portfolio release, the planned setup is a hosted React frontend, a hosted FastAPI backend, and hosted PostgreSQL with `pgvector`. The repository will include deployment instructions and a public demo link when the full upload-to-answer flow works.

## Planned milestones

1. PDF upload, validation, and page-aware text extraction.
2. Chunking, embeddings, and retrieval with PostgreSQL and `pgvector`.
3. Question answering with page references, supporting excerpts, and a small React interface.
4. A bounded agent loop with tools and error handling.
5. Evaluation, safety checks, observability, CI, and deployment.

Each milestone will be implemented and verified in small increments.

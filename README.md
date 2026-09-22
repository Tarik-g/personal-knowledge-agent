# Personal Knowledge Agent (Jarvis Lite)

A personal document assistant built step by step as an Applied AI portfolio project.

## Goal

Upload a PDF, ask a question about it, and receive an answer with a verifiable page reference and supporting excerpt. The first release will use React, FastAPI, PostgreSQL, and `pgvector`.

## Current status

The exact first-release scope and acceptance criteria are documented in [docs/MVP.md](docs/MVP.md). The API extracts page-aware passages from text-based PDFs up to 10 MiB. With a configured database, `POST /documents` saves passages, `GET /documents` lists only the current browser's uploads, and `GET /documents/{id}/chunks` returns their source passages. Retrieval and question answering are planned next.

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

## PostgreSQL without Docker

This project uses hosted PostgreSQL with `pgvector`, so local development and the eventual online demo can connect to the same kind of database. Create a separate [Neon](https://neon.com/) project for Jarvis Lite. In its SQL Editor, run [db/schema.sql](db/schema.sql) once to create the tables. Copy [.env.example](.env.example) to an ignored `.env` file and replace its placeholder `DATABASE_URL` with the project's connection string. The API start command above stays the same.

For a first vector-search exercise, run all of [db/vector_demo.sql](db/vector_demo.sql) together in the SQL Editor. Its three-number vectors are made-up examples, not embeddings calculated from the labels. The real `chunks.embedding` column remains empty until an embedding model is selected. Keep the connection string in `.env` or your hosting provider's secret settings, never in Git.

Each browser receives a random, HTTP-only cookie. The database stores only its hash, and every saved document belongs to that session. Both the document list and source passages filter by it; idle sessions and their documents are deleted on a later database request after 24 hours. Different browsers do not see one another's uploads. Tabs in the same browser share a session, and clearing cookies starts a fresh one. The eventual React interface and API will be served from one HTTPS origin so the browser sends this cookie with requests.

For the portfolio release, the planned setup is a hosted React/FastAPI app and hosted PostgreSQL with `pgvector`. The repository will include deployment instructions and a public demo link when the full upload-to-answer flow works.

## Planned milestones

1. PDF upload, validation, and page-aware text extraction.
2. Chunking, embeddings, and retrieval with PostgreSQL and `pgvector`.
3. Question answering with page references, supporting excerpts, and a small React interface.
4. A bounded agent loop with tools and error handling.
5. Evaluation, safety checks, observability, CI, and deployment.

Each milestone will be implemented and verified in small increments.

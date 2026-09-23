# Personal Knowledge Agent (Jarvis Lite)

Jarvis Lite is a local document assistant and Applied AI portfolio project. Upload a text-based PDF, ask a question, and receive a short answer with the original filename, page number, and supporting passage.

## Current features

- Responsive React interface with PDF drag and drop, loading states, and clear errors.
- PDF validation and page-aware text extraction for files up to 10 MiB.
- Paragraph-aware chunking with overlap and preserved source metadata.
- Local multilingual embeddings with FastEmbed and MiniLM.
- Semantic retrieval using cosine similarity.
- Local answer generation with `qwen3:1.7b` through Ollama.
- Verifiable sources containing filename, page number, and original text.
- A safe no-answer response when retrieval confidence is too low.
- No paid AI API, API key, or per-request charge.
- 18 automated backend checks and a tested end-to-end PDF flow.

The current interface sends one PDF and one question together. The file is processed for that request and is not persisted. PostgreSQL and `pgvector` are prepared as the next step so a document can be uploaded once and questioned repeatedly.

## Technology

| Area | Technology |
| --- | --- |
| Frontend | React 19, Vite 8, CSS |
| API | FastAPI, Python |
| PDF extraction | pypdf |
| Embeddings | FastEmbed, multilingual MiniLM, 384 dimensions |
| Retrieval | Cosine similarity |
| Answer model | Qwen3 1.7B through Ollama |
| Planned persistence | PostgreSQL with `pgvector` |

## How one question is processed

1. React sends the selected PDF and question to `POST /documents/answer`.
2. FastAPI validates the file and extracts text with page numbers.
3. The text is split into overlapping, page-aware passages.
4. FastEmbed converts the question and passages into vectors.
5. Cosine similarity selects the three strongest passages.
6. Ollama gives only those passages to the local Qwen3 model.
7. The API returns the answer and the original source passages.

## Run the current app

### Requirements

- Python 3.11 or newer
- Node.js `20.19+` or `22.12+`
- [Ollama](https://ollama.com/) for the local answer model
- About 1.4 GB of free disk space for `qwen3:1.7b`

The 1.7B model runs on a CPU and is suitable for a computer with 16 GB RAM. A dedicated graphics card is optional.

### One-time setup

Run these commands from the repository root:

```powershell
python -m pip install --user -e .
npm --prefix frontend install
npm --prefix frontend run build
ollama pull qwen3:1.7b
```

On Windows, Ollama can also be installed from the terminal before downloading the model:

```powershell
winget install --id Ollama.Ollama --exact
```

### Start Jarvis Lite

Make sure the Ollama application is running. Then start the complete React and FastAPI app from the repository root with one command:

```powershell
python -m uvicorn jarvis.main:app --reload
```

Open the following addresses:

- App: <http://127.0.0.1:8000/>
- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

The first question can take longer because the embedding and answer models need to load into memory. Later questions are normally faster.

### After changing the frontend

Rebuild the frontend so FastAPI serves the new version:

```powershell
npm --prefix frontend run build
```

For frontend development with instant browser updates, keep FastAPI running and start Vite in a second terminal:

```powershell
npm --prefix frontend run dev
```

Then open <http://127.0.0.1:5173/>. Vite forwards `/api` requests to FastAPI on port 8000.

## Run the checks

Backend checks:

```powershell
python -m unittest discover -s tests -v
```

Frontend production build:

```powershell
npm --prefix frontend run build
```

## Useful API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check whether FastAPI is running |
| `POST` | `/documents/extract` | Extract pages and passages without saving |
| `POST` | `/documents/search` | Return the most relevant PDF passages |
| `POST` | `/documents/answer` | Return a local generated answer with sources |
| `POST` | `/documents` | Save a document when PostgreSQL is configured |
| `GET` | `/documents` | List documents for the anonymous browser session |
| `GET` | `/documents/{id}/chunks` | Read saved passages within the same session |

## Optional database preparation

The complete PDF question flow works without a database today. The files in [`db`](db) prepare the next step: storing documents and 384-dimensional embeddings in hosted PostgreSQL with `pgvector`.

When persistence work begins:

1. Create a separate Neon PostgreSQL project.
2. Run [`db/schema.sql`](db/schema.sql) in its SQL editor.
3. Copy [`.env.example`](.env.example) to an ignored `.env` file.
4. Replace the placeholder `DATABASE_URL` with the private connection string.

Anonymous browser sessions are already implemented. The database stores only a hash of the session cookie, scopes saved documents to that session, and removes data after 24 hours of inactivity.

## Next steps

1. Store chunk embeddings in PostgreSQL with `pgvector`.
2. Upload a PDF once and ask several questions without processing it again.
3. Add retrieval evaluation cases and calibrate the similarity threshold.
4. Add request logging, latency measurement, and local model timing.
5. Prepare CI and a public portfolio deployment.
6. Add the bounded agent loop and tools after the document assistant MVP is stable.

The detailed scope and acceptance criteria live in [`docs/MVP.md`](docs/MVP.md).

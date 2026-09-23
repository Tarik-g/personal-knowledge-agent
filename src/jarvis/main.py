"""HTTP entry point for Jarvis Lite."""

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pypdf.errors import PdfReadError
import psycopg

from jarvis import database
from jarvis.answering import generate_answer_from_chunks
from jarvis.chunking import chunk_pages
from jarvis.embeddings import LocalEmbeddingModel
from jarvis.generation import (
    AnswerGenerationFailed,
    AnswerGenerationNotConfigured,
    OllamaAnswerGenerator,
)
from jarvis.pdf import extract_pages_from_stream
from jarvis.retrieval import find_relevant_chunks
from jarvis.sessions import DemoSessionId

app = FastAPI(title="Jarvis Lite", version="0.1.0")
MAX_PDF_BYTES = 10 * 1024 * 1024
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
embedding_model = LocalEmbeddingModel()
answer_generator = OllamaAnswerGenerator()

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


@app.get("/", include_in_schema=False, response_model=None)
def root() -> FileResponse | RedirectResponse:
    """Open the built frontend, or API documentation before it exists."""
    index = FRONTEND_DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is ready to receive requests."""
    return {"status": "ok"}


@app.post("/documents/extract")
def extract_document(file: Annotated[UploadFile, File()]) -> dict:
    """Read a PDF without saving it; useful for checking extraction locally."""
    return _extract_document(file)


@app.post("/documents/search")
def search_document(
    file: Annotated[UploadFile, File()],
    question: Annotated[str, Form()],
    limit: Annotated[int, Form(ge=1, le=5)] = 3,
) -> dict:
    """Find PDF passages whose meaning is closest to the question."""
    extracted = _extract_document(file)
    try:
        matches = find_relevant_chunks(
            question,
            extracted["abschnitte"],
            embedding_model,
            limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "frage": question.strip(),
        "dateiname": extracted["dateiname"],
        "treffer": matches,
    }


@app.post("/documents/answer")
def answer_document_question(
    file: Annotated[UploadFile, File()],
    question: Annotated[str, Form()],
) -> dict:
    """Answer from the best supported PDF passage and cite its source."""
    extracted = _extract_document(file)
    try:
        result = generate_answer_from_chunks(
            question,
            extracted["abschnitte"],
            embedding_model,
            answer_generator,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AnswerGenerationNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AnswerGenerationFailed as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "frage": question.strip(),
        "dateiname": extracted["dateiname"],
        **result,
    }


@app.post("/documents", status_code=201)
def upload_document(
    file: Annotated[UploadFile, File()], session_id: DemoSessionId
) -> dict:
    """Save a PDF's passages for this browser's private demo session."""
    extracted = _extract_document(file)
    try:
        document_id = database.save_document(
            session_id,
            extracted["dateiname"],
            extracted["seiten"],
            extracted["abschnitte"],
        )
    except (database.DatabaseNotConfigured, psycopg.Error) as exc:
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar.") from exc

    return {
        "id": document_id,
        "dateiname": extracted["dateiname"],
        "seitenanzahl": extracted["seitenanzahl"],
        "abschnittanzahl": len(extracted["abschnitte"]),
    }


@app.get("/documents")
def list_saved_documents(session_id: DemoSessionId) -> dict:
    """Show only documents uploaded in this browser's demo session."""
    try:
        documents = database.list_documents(session_id)
    except (database.DatabaseNotConfigured, psycopg.Error) as exc:
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar.") from exc
    return {"documents": documents}


@app.get("/documents/{document_id}/chunks")
def get_saved_document_chunks(document_id: UUID, session_id: DemoSessionId) -> dict:
    """Return a document's source passages only to its uploading browser."""
    try:
        chunks = database.get_document_chunks(session_id, document_id)
    except (database.DatabaseNotConfigured, psycopg.Error) as exc:
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar.") from exc
    if not chunks:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden.")
    return {"chunks": chunks}


def _extract_document(file: UploadFile) -> dict:
    """Validate the uploaded PDF and keep text with its source page."""
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Bitte eine PDF-Datei hochladen.")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="Das PDF darf höchstens 10 MiB groß sein.")

    try:
        pages = extract_pages_from_stream(file.file, filename)
    except (PdfReadError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "dateiname": filename,
        "seitenanzahl": len(pages),
        "seiten": pages,
        "abschnitte": chunk_pages(pages),
    }

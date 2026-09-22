"""HTTP entry point for Jarvis Lite."""

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from pypdf.errors import PdfReadError

from jarvis.chunking import chunk_pages
from jarvis.pdf import extract_pages_from_stream

app = FastAPI(title="Jarvis Lite", version="0.1.0")
MAX_PDF_BYTES = 10 * 1024 * 1024


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Open the API documentation from the base URL."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is ready to receive requests."""
    return {"status": "ok"}


@app.post("/documents/extract")
def extract_document(file: Annotated[UploadFile, File()]) -> dict:
    """Read a text-based PDF and return its content with page numbers."""
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

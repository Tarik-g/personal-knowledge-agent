"""Read PDF text while keeping its source page."""

from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader


def extract_pages(pdf_path: str | Path) -> list[dict[str, str | int]]:
    """Return one dictionary per PDF page with filename, page number, and text."""
    path = Path(pdf_path)
    with path.open("rb") as pdf_file:
        return extract_pages_from_stream(pdf_file, path.name)


def extract_pages_from_stream(
    pdf_file: BinaryIO, filename: str
) -> list[dict[str, str | int]]:
    """Extract pages from an already opened PDF, such as a FastAPI upload."""
    reader = PdfReader(pdf_file)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        pages.append(
            {
                "dateiname": filename,
                "seitenzahl": page_number,
                "text": (page.extract_text() or "").strip(),
            }
        )

    if not any(page["text"] for page in pages):
        raise ValueError("Das PDF enthält keinen auslesbaren Text.")

    return pages

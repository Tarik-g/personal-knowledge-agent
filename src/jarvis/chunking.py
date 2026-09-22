"""Split extracted PDF pages into searchable text passages."""

import re


def chunk_pages(
    pages: list[dict[str, str | int]],
    max_chars: int = 1000,
    overlap_chars: int = 150,
) -> list[dict[str, str | int]]:
    """Split each page into passages and keep its filename and page number."""
    if max_chars < 2:
        raise ValueError("max_chars muss mindestens 2 sein.")
    if not 0 <= overlap_chars < max_chars // 2:
        raise ValueError("overlap_chars muss zwischen 0 und der halben Abschnittslänge liegen.")

    chunks = []
    for page in pages:
        text = str(page["text"]).replace("\r\n", "\n").strip()
        if not text:
            continue

        for number, passage in enumerate(
            _split_text(text, max_chars, overlap_chars), start=1
        ):
            chunks.append(
                {
                    "dateiname": str(page["dateiname"]),
                    "seitenzahl": int(page["seitenzahl"]),
                    "abschnitt_nummer": number,
                    "text": passage,
                }
            )

    return chunks


def _split_text(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    passages = []
    start = 0

    while start < len(text):
        limit = min(start + max_chars, len(text))
        end = limit if limit == len(text) else _find_break(text[start:limit], start)
        passage = text[start:end].strip()
        if passage:
            passages.append(passage)
        if end == len(text):
            break

        next_start = end - overlap_chars
        if next_start <= start:
            next_start = end
        else:
            while next_start < end and not text[next_start - 1].isspace():
                next_start += 1
        while next_start < len(text) and text[next_start].isspace():
            next_start += 1
        start = next_start

    return passages


def _find_break(window: str, offset: int) -> int:
    """Prefer a paragraph, then a sentence, then a word near the size limit."""
    minimum = len(window) // 2
    for pattern in (r"\n\s*\n", r"[.!?]\s+", r"\s+"):
        endings = [
            match.end()
            for match in re.finditer(pattern, window)
            if match.end() >= minimum
        ]
        if endings:
            return offset + endings[-1]
    return offset + len(window)

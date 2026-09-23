"""Rank PDF passages by their semantic similarity to a question."""

from math import sqrt
from typing import Sequence

from jarvis.embeddings import EmbeddingModel


def cosine_similarity(first: Sequence[float], second: Sequence[float]) -> float:
    """Return the angle-based similarity of two equally sized vectors."""
    if not first or len(first) != len(second):
        raise ValueError("Die Vektoren müssen gleich lang und dürfen nicht leer sein.")

    first_norm = sqrt(sum(value * value for value in first))
    second_norm = sqrt(sum(value * value for value in second))
    if first_norm == 0 or second_norm == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))
    return dot_product / (first_norm * second_norm)


def find_relevant_chunks(
    question: str,
    chunks: Sequence[dict[str, str | int]],
    model: EmbeddingModel,
    limit: int = 3,
) -> list[dict[str, str | int | float]]:
    """Return the most relevant chunks while preserving their source metadata."""
    if not question.strip():
        raise ValueError("Die Frage darf nicht leer sein.")
    if limit < 1:
        raise ValueError("limit muss mindestens 1 sein.")
    if not chunks:
        return []

    query_vector = model.embed_query(question.strip())
    document_vectors = model.embed_documents([str(chunk["text"]) for chunk in chunks])
    if len(document_vectors) != len(chunks):
        raise ValueError("Das Embedding-Modell lieferte nicht für jeden Abschnitt einen Vektor.")

    ranked = []
    for chunk, vector in zip(chunks, document_vectors):
        ranked.append(
            {
                **chunk,
                "aehnlichkeit": cosine_similarity(query_vector, vector),
            }
        )

    ranked.sort(key=lambda chunk: float(chunk["aehnlichkeit"]), reverse=True)
    return ranked[:limit]

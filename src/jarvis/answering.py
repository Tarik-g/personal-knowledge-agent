"""Build a verifiable answer from retrieved PDF passages."""

from typing import Sequence

from jarvis.embeddings import EmbeddingModel
from jarvis.generation import AnswerGenerator
from jarvis.retrieval import find_relevant_chunks

MINIMUM_SIMILARITY = 0.25
NO_ANSWER = "Ich konnte dazu keine ausreichend passende Stelle im PDF finden."


def answer_from_chunks(
    question: str,
    chunks: Sequence[dict[str, str | int]],
    model: EmbeddingModel,
    minimum_similarity: float = MINIMUM_SIMILARITY,
) -> dict:
    """Return the best supported passage as an answer with its source."""
    matches = find_relevant_chunks(question, chunks, model, limit=1)
    if not matches or float(matches[0]["aehnlichkeit"]) < minimum_similarity:
        return {"antwort": NO_ANSWER, "quellen": []}

    best_match = matches[0]
    return {
        "antwort": str(best_match["text"]),
        "quellen": [_format_source(best_match)],
    }


def generate_answer_from_chunks(
    question: str,
    chunks: Sequence[dict[str, str | int]],
    embedding_model: EmbeddingModel,
    answer_generator: AnswerGenerator,
    minimum_similarity: float = MINIMUM_SIMILARITY,
) -> dict:
    """Retrieve passages, then generate an answer using only those passages."""
    matches = find_relevant_chunks(question, chunks, embedding_model, limit=3)
    if not matches or float(matches[0]["aehnlichkeit"]) < minimum_similarity:
        return {"antwort": NO_ANSWER, "quellen": []}

    answer = answer_generator.generate(question.strip(), matches)
    if answer == NO_ANSWER:
        return {"antwort": NO_ANSWER, "quellen": []}

    return {
        "antwort": answer,
        "quellen": [_format_source(match) for match in matches],
    }


def _format_source(source: dict[str, str | int | float]) -> dict:
    """Expose one consistent source shape to the API and future frontend."""
    return {
        "dateiname": source["dateiname"],
        "seitenzahl": source["seitenzahl"],
        "abschnitt_nummer": source["abschnitt_nummer"],
        "inhalt": source["text"],
        "aehnlichkeit": source["aehnlichkeit"],
    }

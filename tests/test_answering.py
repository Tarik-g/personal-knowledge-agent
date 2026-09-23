"""Answers must remain tied to a retrieved PDF source."""

import unittest

from jarvis.answering import NO_ANSWER, answer_from_chunks, generate_answer_from_chunks


class FakeEmbeddingModel:
    vectors = {
        "Warum ist das Auto in der Werkstatt?": [1.0, 0.0],
        "Das Auto hat einen Motorschaden.": [0.9, 0.1],
        "Was kostet die Reise?": [0.0, 1.0],
    }

    def embed_query(self, text: str) -> list[float]:
        return self.vectors[text]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.vectors[text] for text in texts]


class FakeAnswerGenerator:
    def __init__(self) -> None:
        self.calls = []

    def generate(self, question: str, sources: list[dict]) -> str:
        self.calls.append((question, sources))
        return "Das Auto ist wegen eines Motorschadens in der Werkstatt. [Quelle 1]"


class AnsweringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = [
            {
                "dateiname": "bericht.pdf",
                "seitenzahl": 4,
                "abschnitt_nummer": 2,
                "text": "Das Auto hat einen Motorschaden.",
            }
        ]
        self.model = FakeEmbeddingModel()

    def test_supported_answer_contains_filename_page_and_excerpt(self) -> None:
        result = answer_from_chunks(
            "Warum ist das Auto in der Werkstatt?",
            self.chunks,
            self.model,
        )

        self.assertEqual(result["antwort"], "Das Auto hat einen Motorschaden.")
        self.assertEqual(result["quellen"][0]["dateiname"], "bericht.pdf")
        self.assertEqual(result["quellen"][0]["seitenzahl"], 4)
        self.assertEqual(
            result["quellen"][0]["inhalt"],
            "Das Auto hat einen Motorschaden.",
        )

    def test_unsupported_answer_has_no_invented_source(self) -> None:
        result = answer_from_chunks(
            "Was kostet die Reise?",
            self.chunks,
            self.model,
        )

        self.assertEqual(result, {"antwort": NO_ANSWER, "quellen": []})

    def test_generated_answer_receives_only_retrieved_sources(self) -> None:
        generator = FakeAnswerGenerator()

        result = generate_answer_from_chunks(
            "Warum ist das Auto in der Werkstatt?",
            self.chunks,
            self.model,
            generator,
        )

        self.assertEqual(
            result["antwort"],
            "Das Auto ist wegen eines Motorschadens in der Werkstatt. [Quelle 1]",
        )
        self.assertEqual(len(generator.calls), 1)
        self.assertEqual(generator.calls[0][1][0]["text"], self.chunks[0]["text"])
        self.assertEqual(result["quellen"][0]["seitenzahl"], 4)

    def test_generation_is_skipped_when_retrieval_is_too_weak(self) -> None:
        generator = FakeAnswerGenerator()

        result = generate_answer_from_chunks(
            "Was kostet die Reise?",
            self.chunks,
            self.model,
            generator,
        )

        self.assertEqual(result, {"antwort": NO_ANSWER, "quellen": []})
        self.assertEqual(generator.calls, [])


if __name__ == "__main__":
    unittest.main()

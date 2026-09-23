"""The search API connects PDF chunks with semantic retrieval."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from jarvis.main import app


class FakeEmbeddingModel:
    vectors = {
        "Warum muss das Auto repariert werden?": [1.0, 0.0],
        "Das Auto hat einen Motorschaden.": [0.9, 0.1],
        "Für den Kuchen brauchen wir Mehl.": [0.0, 1.0],
    }

    def embed_query(self, text: str) -> list[float]:
        return self.vectors[text]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.vectors[text] for text in texts]


class FakeAnswerGenerator:
    def generate(self, question: str, sources: list[dict]) -> str:
        return "Das Auto muss wegen eines Motorschadens repariert werden. [Quelle 1]"


class SearchApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extracted = {
            "dateiname": "bericht.pdf",
            "seitenanzahl": 2,
            "seiten": [],
            "abschnitte": [
                {
                    "dateiname": "bericht.pdf",
                    "seitenzahl": 2,
                    "abschnitt_nummer": 1,
                    "text": "Das Auto hat einen Motorschaden.",
                },
                {
                    "dateiname": "bericht.pdf",
                    "seitenzahl": 1,
                    "abschnitt_nummer": 1,
                    "text": "Für den Kuchen brauchen wir Mehl.",
                },
            ],
        }

    def test_search_returns_the_best_passage_with_its_source(self) -> None:
        with (
            patch("jarvis.main._extract_document", return_value=self.extracted),
            patch("jarvis.main.embedding_model", FakeEmbeddingModel()),
            TestClient(app) as client,
        ):
            response = client.post(
                "/documents/search",
                files={"file": ("bericht.pdf", b"PDF", "application/pdf")},
                data={
                    "question": "Warum muss das Auto repariert werden?",
                    "limit": "1",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["frage"], "Warum muss das Auto repariert werden?")
        self.assertEqual(body["dateiname"], "bericht.pdf")
        self.assertEqual(len(body["treffer"]), 1)
        self.assertEqual(body["treffer"][0]["seitenzahl"], 2)
        self.assertEqual(
            body["treffer"][0]["text"],
            "Das Auto hat einen Motorschaden.",
        )

    def test_answer_returns_generated_text_and_page_source(self) -> None:
        with (
            patch("jarvis.main._extract_document", return_value=self.extracted),
            patch("jarvis.main.embedding_model", FakeEmbeddingModel()),
            patch("jarvis.main.answer_generator", FakeAnswerGenerator()),
            TestClient(app) as client,
        ):
            response = client.post(
                "/documents/answer",
                files={"file": ("bericht.pdf", b"PDF", "application/pdf")},
                data={"question": "Warum muss das Auto repariert werden?"},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            body["antwort"],
            "Das Auto muss wegen eines Motorschadens repariert werden. [Quelle 1]",
        )
        self.assertEqual(body["quellen"][0]["dateiname"], "bericht.pdf")
        self.assertEqual(body["quellen"][0]["seitenzahl"], 2)


if __name__ == "__main__":
    unittest.main()

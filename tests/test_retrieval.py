"""Checks for semantic passage ranking without downloading a real model."""

import unittest

from jarvis.retrieval import cosine_similarity, find_relevant_chunks


class FakeEmbeddingModel:
    """Predictable vectors keep retrieval tests fast and understandable."""

    vectors = {
        "Welches Fahrzeug braucht eine Reparatur?": [1.0, 0.0],
        "Der rote Wagen hat einen Motorschaden.": [0.9, 0.1],
        "Das Rezept benötigt Mehl und Butter.": [0.0, 1.0],
    }

    def embed_query(self, text: str) -> list[float]:
        return self.vectors[text]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.vectors[text] for text in texts]


class RetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = [
            {
                "dateiname": "bericht.pdf",
                "seitenzahl": 7,
                "abschnitt_nummer": 2,
                "text": "Der rote Wagen hat einen Motorschaden.",
            },
            {
                "dateiname": "kochbuch.pdf",
                "seitenzahl": 3,
                "abschnitt_nummer": 1,
                "text": "Das Rezept benötigt Mehl und Butter.",
            },
        ]

    def test_cosine_similarity_compares_vector_direction(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_most_similar_chunk_keeps_its_source(self) -> None:
        results = find_relevant_chunks(
            "Welches Fahrzeug braucht eine Reparatur?",
            self.chunks,
            FakeEmbeddingModel(),
            limit=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["dateiname"], "bericht.pdf")
        self.assertEqual(results[0]["seitenzahl"], 7)
        self.assertEqual(results[0]["abschnitt_nummer"], 2)
        self.assertGreater(results[0]["aehnlichkeit"], 0.9)

    def test_empty_question_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            find_relevant_chunks("  ", self.chunks, FakeEmbeddingModel())

    def test_empty_chunk_list_needs_no_model_call(self) -> None:
        self.assertEqual(
            find_relevant_chunks("Eine Frage", [], FakeEmbeddingModel()),
            [],
        )


if __name__ == "__main__":
    unittest.main()

"""Checks for page-aware text chunking."""

import unittest

from jarvis.chunking import chunk_pages


class ChunkPagesTests(unittest.TestCase):
    def test_prefers_paragraph_boundary(self) -> None:
        pages = [
            {
                "dateiname": "notizen.pdf",
                "seitenzahl": 3,
                "text": "Alpha words stay together.\n\nBeta words start a new paragraph.",
            }
        ]

        chunks = chunk_pages(pages, max_chars=45, overlap_chars=0)

        self.assertEqual(chunks[0]["text"], "Alpha words stay together.")
        self.assertEqual(chunks[1]["text"], "Beta words start a new paragraph.")
        self.assertEqual([chunk["abschnitt_nummer"] for chunk in chunks], [1, 2])
        self.assertTrue(all(chunk["seitenzahl"] == 3 for chunk in chunks))

    def test_overlap_keeps_words_at_boundary(self) -> None:
        words = [f"word{number:02d}" for number in range(20)]
        pages = [
            {"dateiname": "notizen.pdf", "seitenzahl": 1, "text": " ".join(words)},
            {"dateiname": "notizen.pdf", "seitenzahl": 2, "text": ""},
        ]

        chunks = chunk_pages(pages, max_chars=40, overlap_chars=10)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk["text"]) <= 40 for chunk in chunks))
        self.assertTrue(all(chunk["dateiname"] == "notizen.pdf" for chunk in chunks))
        self.assertTrue(all(chunk["seitenzahl"] == 1 for chunk in chunks))
        self.assertEqual(set(words), set().union(*(set(chunk["text"].split()) for chunk in chunks)))
        self.assertTrue(set(chunks[0]["text"].split()) & set(chunks[1]["text"].split()))

    def test_rejects_overlap_that_prevents_progress(self) -> None:
        with self.assertRaises(ValueError):
            chunk_pages([], max_chars=40, overlap_chars=20)


if __name__ == "__main__":
    unittest.main()

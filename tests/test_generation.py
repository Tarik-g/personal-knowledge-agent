"""The local answer generator sends only grounded context to Ollama."""

import unittest
from unittest.mock import patch

import httpx

from jarvis.generation import AnswerGenerationNotConfigured, OllamaAnswerGenerator


class OllamaGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = [
            {
                "dateiname": "bericht.pdf",
                "seitenzahl": 2,
                "abschnitt_nummer": 1,
                "text": "Das Auto hat einen Motorschaden.",
                "aehnlichkeit": 0.9,
            }
        ]

    @patch("jarvis.generation.httpx.post")
    def test_local_model_receives_question_and_source(self, post) -> None:
        post.return_value = httpx.Response(
            200,
            json={
                "message": {
                    "content": "Das Auto ist wegen eines Motorschadens dort. [Quelle 1]"
                }
            },
            request=httpx.Request("POST", "http://localhost/api/chat"),
        )
        generator = OllamaAnswerGenerator(
            model_name="qwen3:1.7b",
            base_url="http://localhost/",
        )

        answer = generator.generate("Warum ist das Auto dort?", self.sources)

        self.assertEqual(
            answer,
            "Das Auto ist wegen eines Motorschadens dort. [Quelle 1]",
        )
        request = post.call_args
        self.assertEqual(request.args[0], "http://localhost/api/chat")
        self.assertEqual(request.kwargs["json"]["model"], "qwen3:1.7b")
        self.assertIn("Seite 2", request.kwargs["json"]["messages"][1]["content"])
        self.assertFalse(request.kwargs["json"]["think"])

    @patch("jarvis.generation.httpx.post")
    def test_missing_local_server_returns_clear_error(self, post) -> None:
        post.side_effect = httpx.ConnectError("connection refused")

        with self.assertRaisesRegex(AnswerGenerationNotConfigured, "Ollama"):
            OllamaAnswerGenerator().generate("Eine Frage", self.sources)


if __name__ == "__main__":
    unittest.main()

"""A shared API routes each visitor to a different document scope."""

from hashlib import sha256
import unittest
from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient

from jarvis.main import app


class DemoIsolationTests(unittest.TestCase):
    def test_two_browsers_keep_separate_document_lists(self) -> None:
        documents_by_session: dict[str, list[dict[str, str]]] = {}
        first_session = ""
        document_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")

        def documents_for(session_id: str) -> list[dict[str, str]]:
            return documents_by_session.get(session_id, [])

        def chunks_for(session_id: str, requested_id: UUID) -> list[dict]:
            if session_id == first_session and requested_id == document_id:
                return [{"filename": "nur-fuer-a.pdf", "page_number": 1, "content": "A"}]
            return []

        with (
            patch("jarvis.main.database.list_documents", side_effect=documents_for),
            patch("jarvis.main.database.get_document_chunks", side_effect=chunks_for),
        ):
            with (
                TestClient(app, base_url="https://testserver") as first_browser,
                TestClient(app, base_url="https://testserver") as second_browser,
            ):
                first_browser.get("/documents")
                second_browser.get("/documents")

                first_cookie = first_browser.cookies.get("jarvis_demo_session")
                second_cookie = second_browser.cookies.get("jarvis_demo_session")
                self.assertIsNotNone(first_cookie)
                self.assertIsNotNone(second_cookie)
                self.assertNotEqual(first_cookie, second_cookie)

                first_session = sha256(first_cookie.encode("ascii")).hexdigest()
                documents_by_session[first_session] = [{"filename": "nur-fuer-a.pdf"}]

                first_response = first_browser.get("/documents")
                second_response = second_browser.get("/documents")
                first_chunks = first_browser.get(f"/documents/{document_id}/chunks")
                second_chunks = second_browser.get(f"/documents/{document_id}/chunks")

        self.assertEqual(
            first_response.json(), {"documents": [{"filename": "nur-fuer-a.pdf"}]}
        )
        self.assertEqual(second_response.json(), {"documents": []})
        self.assertEqual(first_chunks.status_code, 200)
        self.assertEqual(second_chunks.status_code, 404)


if __name__ == "__main__":
    unittest.main()

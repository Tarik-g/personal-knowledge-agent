"""Browser identity stays private and separate for each visitor."""

import hashlib
import unittest
from http.cookies import SimpleCookie

from starlette.requests import Request
from starlette.responses import Response

from jarvis.sessions import COOKIE_NAME, get_session_id


def make_request(cookie: str | None = None) -> Request:
    headers = [] if cookie is None else [(b"cookie", cookie.encode("ascii"))]
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/documents",
            "scheme": "http",
            "headers": headers,
        }
    )


class DemoSessionTests(unittest.TestCase):
    def test_browsers_get_distinct_private_cookies(self) -> None:
        first_response = Response()
        first_id = get_session_id(make_request(), first_response)
        second_response = Response()
        second_id = get_session_id(make_request(), second_response)

        self.assertNotEqual(first_id, second_id)
        cookie_header = first_response.headers["set-cookie"]
        self.assertIn("httponly", cookie_header.lower())
        self.assertIn("secure", cookie_header.lower())
        self.assertIn("samesite=lax", cookie_header.lower())
        cookies = SimpleCookie()
        cookies.load(cookie_header)
        token = cookies[COOKIE_NAME].value
        self.assertEqual(first_id, hashlib.sha256(token.encode("ascii")).hexdigest())
        self.assertNotEqual(first_id, token)

        returning_response = Response()
        returning_id = get_session_id(
            make_request(f"{COOKIE_NAME}={token}"), returning_response
        )
        self.assertEqual(first_id, returning_id)
        self.assertNotIn("set-cookie", returning_response.headers)

    def test_invalid_cookie_is_replaced(self) -> None:
        response = Response()
        get_session_id(make_request(f"{COOKIE_NAME}=not-a-session"), response)
        self.assertIn("set-cookie", response.headers)


if __name__ == "__main__":
    unittest.main()

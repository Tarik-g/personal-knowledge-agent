"""Anonymous browser sessions for the public document demo."""

import hashlib
import re
import secrets
from typing import Annotated

from fastapi import Depends, Request, Response

COOKIE_NAME = "jarvis_demo_session"
SESSION_LIFETIME_SECONDS = 24 * 60 * 60
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")


def get_session_id(request: Request, response: Response) -> str:
    """Return a database key derived from a secret, browser-only cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if token is None or _TOKEN_PATTERN.fullmatch(token) is None:
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=SESSION_LIFETIME_SECONDS,
            httponly=True,
            secure=request.url.hostname not in {"localhost", "127.0.0.1", "::1"},
            samesite="lax",
            path="/",
        )

    return hashlib.sha256(token.encode("ascii")).hexdigest()


DemoSessionId = Annotated[str, Depends(get_session_id)]

"""HTTP entry point for Jarvis Lite."""

from fastapi import FastAPI

app = FastAPI(title="Jarvis Lite", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is ready to receive requests."""
    return {"status": "ok"}

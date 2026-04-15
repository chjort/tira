"""FastAPI application for the TIRA Task Queue Backend."""

from fastapi import FastAPI

from task_queue_backend.routers import research

app = FastAPI(title="TIRA Task Queue Backend", version="0.1.0")
app.include_router(research.router, prefix="/research", tags=["research"])


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}

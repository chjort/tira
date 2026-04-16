"""FastAPI application for the TIRA Task Queue Backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from task_queue_backend.config import settings
from task_queue_backend.routers import research
from task_queue_backend.task_registry import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application-level resources (Redis client)."""
    app.state.redis = get_redis_client(settings.redis_url)
    yield
    app.state.redis.close()


app = FastAPI(title="TIRA Task Queue Backend", version="0.1.0", lifespan=lifespan)
app.include_router(research.router, prefix="/research", tags=["research"])


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}

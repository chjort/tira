"""Celery task definitions for the research agent worker."""

import asyncio

from celery import signals

from agent_worker.agent import run_research
from agent_worker.celery_app import app
from agent_worker.tracing import configure_tracing


@signals.worker_init.connect
def on_worker_init(**kwargs):
    """Configure MLflow tracing once when the worker process starts."""
    configure_tracing()


@app.task(
    bind=True,
    name="agent_worker.tasks.run_research_task",
    max_retries=2,
    default_retry_delay=30,
)
def run_research_task(self, theme: str) -> str:
    """Run the async research agent and return a Markdown report.

    Uses asyncio.run() to bridge the sync Celery task with the async Agent SDK.
    Each invocation creates a fresh event loop, which is safe with --pool=threads.

    Args:
        theme: The investment theme to research.

    Returns:
        Markdown report string, stored in the Celery result backend.
    """
    try:
        return asyncio.run(run_research(theme))
    except Exception as exc:
        raise self.retry(exc=exc)

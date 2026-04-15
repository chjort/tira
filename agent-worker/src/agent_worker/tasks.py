"""Celery task definitions for the research agent worker."""

import asyncio
import logging

from celery import signals

from agent_worker import config
from agent_worker.agent import run_research
from agent_worker.celery_app import app
from agent_worker.evaluation.simple_eval import run_evaluation
from agent_worker.tracing import configure_tracing

logger = logging.getLogger(__name__)


@signals.worker_init.connect
def on_worker_init(**kwargs):
    """Configure MLflow tracing once when the worker process starts."""
    configure_tracing()


def _evaluate_report(theme: str, report: str) -> None:
    """Run MLflow evaluation suites if evaluation is enabled.

    Delegates to :func:`run_evaluation`, catching all exceptions so that
    evaluation failures never cause the Celery task to fail or retry.

    Args:
        theme: The investment theme that was researched.
        report: The Markdown report to evaluate.
    """
    if not config.EVAL_ENABLED:
        return
    try:
        run_evaluation(theme, report, suite_names=config.EVAL_SUITES)
    except Exception:
        logger.exception("Evaluation failed for theme %r; skipping.", theme)


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

    After the report is generated, evaluation suites are run as a side-effect
    (logged to MLflow). Evaluation failures are silenced so they never trigger
    task retries.

    Args:
        theme: The investment theme to research.

    Returns:
        Markdown report string, stored in the Celery result backend.
    """
    try:
        report = asyncio.run(run_research(theme))
    except Exception as exc:
        raise self.retry(exc=exc)

    _evaluate_report(theme, report)
    return report

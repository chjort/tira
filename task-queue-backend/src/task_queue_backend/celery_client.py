"""Client-only Celery instance for dispatching tasks to the agent worker.

This module does NOT import any agent_worker code. The only coupling between
services is the task name string.
"""

from celery import Celery
from task_queue_backend.config import settings

celery_client = Celery(
    "task_queue_backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_client.config_from_object(
    {
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
    }
)

RESEARCH_TASK_NAME = "agent_worker.tasks.run_research_task"

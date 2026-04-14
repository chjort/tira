"""Celery application instance and configuration for the agent worker."""

from celery import Celery

from agent_worker import config

app = Celery("agent_worker")
app.config_from_object(
    {
        "broker_url": config.CELERY_BROKER_URL,
        "result_backend": config.CELERY_RESULT_BACKEND,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "task_track_started": True,
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
    }
)
app.autodiscover_tasks(["agent_worker"])

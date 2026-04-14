"""MLflow tracing configuration for OpenAI agent calls."""

import mlflow

from agent_worker import config


def configure_tracing() -> None:
    """Set up MLflow experiment tracking and OpenAI autologging.

    Called once at worker startup via the Celery worker_init signal.
    """
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT_NAME)
    mlflow.openai.autolog()

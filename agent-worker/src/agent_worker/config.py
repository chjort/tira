"""Configuration for the Research Agent Worker, read from environment variables."""

import os

CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND: str = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
)
MLFLOW_TRACKING_URI: str = os.environ.get(
    "MLFLOW_TRACKING_URI", "http://localhost:5000"
)
MLFLOW_EXPERIMENT_NAME: str = os.environ.get(
    "MLFLOW_EXPERIMENT_NAME", "TIRA Research Agent"
)
OPENAI_BASE_URL: str = os.environ.get(
    "OPENAI_BASE_URL", "https://api.marketplace.novo-genai.com/v1"
)
EVAL_JUDGE_MODEL: str = os.environ.get("EVAL_JUDGE_MODEL", "openai_gpt52")
EVAL_ENABLED: bool = os.environ.get("EVAL_ENABLED", "false").lower() == "true"
EVAL_SUITES: list[str] = [
    s.strip()
    for s in os.environ.get(
        "EVAL_SUITES",
        "groundedness,source_quality,coverage,factual_accuracy",
    ).split(",")
    if s.strip()
]

"""Configuration for the Task Queue Backend, using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings read from environment variables."""

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    @property
    def redis_url(self) -> str:
        """Redis URL for the task registry (same instance as the Celery broker)."""
        return self.celery_broker_url


settings = Settings()

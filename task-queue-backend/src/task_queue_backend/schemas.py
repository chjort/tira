"""Pydantic request and response models for the research API."""

from typing import Literal

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    """Request body for submitting a new research task."""

    theme: str


class TaskSubmittedResponse(BaseModel):
    """Response after successfully submitting a research task."""

    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    """Response for task status and result queries."""

    task_id: str
    status: Literal["PENDING", "STARTED", "SUCCESS", "FAILURE", "RETRY", "REVOKED"]
    result: str | None = None
    error: str | None = None

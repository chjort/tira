"""REST API endpoints for submitting and querying research tasks."""

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Request

from task_queue_backend.celery_client import RESEARCH_TASK_NAME, celery_client
from task_queue_backend.schemas import (
    ResearchRequest,
    TaskListResponse,
    TaskStatusResponse,
    TaskSubmittedResponse,
)
from task_queue_backend.task_registry import list_tasks, register_task

router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_research_tasks(request: Request) -> TaskListResponse:
    """List all submitted research tasks."""
    tasks = list_tasks(request.app.state.redis)
    return TaskListResponse(tasks=tasks)


@router.post("", response_model=TaskSubmittedResponse)
async def submit_research(
    request: Request,
    body: ResearchRequest,
) -> TaskSubmittedResponse:
    """Submit a new thematic investment research task."""
    result = celery_client.send_task(RESEARCH_TASK_NAME, args=[body.theme])
    register_task(request.app.state.redis, result.id, body.theme)
    return TaskSubmittedResponse(task_id=result.id, status="PENDING")


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Check the status of a research task."""
    result = AsyncResult(task_id, app=celery_client)
    status = result.status

    response = TaskStatusResponse(task_id=task_id, status=status)

    if status == "FAILURE":
        response.error = str(result.result)

    return response


@router.get("/{task_id}/result", response_model=TaskStatusResponse)
async def get_task_result(task_id: str) -> TaskStatusResponse:
    """Retrieve the completed research report."""
    result = AsyncResult(task_id, app=celery_client)
    status = result.status

    if status != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"Task is not complete. Current status: {status}",
        )

    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        result=result.result,
    )

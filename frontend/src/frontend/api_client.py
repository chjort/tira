"""HTTP client for communicating with the Task Queue Backend API."""

import httpx

from frontend.config import BACKEND_URL


def submit_research(theme: str) -> dict:
    """Submit a new research task.

    Args:
        theme: The investment theme to research.

    Returns:
        Dict with 'task_id' and 'status' keys.
    """
    response = httpx.post(f"{BACKEND_URL}/research", json={"theme": theme}, timeout=10)
    response.raise_for_status()
    return response.json()


def get_status(task_id: str) -> dict:
    """Poll the status of a research task.

    Args:
        task_id: The Celery task ID.

    Returns:
        Dict with 'task_id', 'status', and optionally 'error' keys.
    """
    response = httpx.get(f"{BACKEND_URL}/research/{task_id}/status", timeout=10)
    response.raise_for_status()
    return response.json()


def get_result(task_id: str) -> dict:
    """Retrieve the completed research report.

    Args:
        task_id: The Celery task ID.

    Returns:
        Dict with 'task_id', 'status', and 'result' (Markdown report) keys.
    """
    response = httpx.get(f"{BACKEND_URL}/research/{task_id}/result", timeout=30)
    response.raise_for_status()
    return response.json()

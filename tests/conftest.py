"""Shared fixtures for E2E and integration tests."""

import os
import time

import httpx
import pytest


@pytest.fixture
def backend_url() -> str:
    """Base URL of the Task Queue Backend service."""
    return os.environ.get("BACKEND_URL", "http://localhost:8000")


@pytest.fixture
def http_client() -> httpx.Client:
    """HTTP client for making API requests."""
    with httpx.Client(timeout=30) as client:
        yield client


@pytest.fixture
def wait_for_task(http_client: httpx.Client, backend_url: str):
    """Factory fixture that polls a task until it reaches a terminal state.

    Returns a callable: wait_for_task(task_id, timeout=300) -> final_status
    """

    def _wait(task_id: str, timeout: int = 300) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            resp = http_client.get(f"{backend_url}/research/{task_id}/status")
            resp.raise_for_status()
            status = resp.json()["status"]
            if status in ("SUCCESS", "FAILURE", "REVOKED"):
                return status
            time.sleep(5)
        raise TimeoutError(
            f"Task {task_id} did not complete within {timeout}s. Last status: {status}"
        )

    return _wait

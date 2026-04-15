"""End-to-end tests for the TIRA research pipeline.

These tests require all services running via `docker compose up`.
Run with: uv run pytest tests/ -m e2e -v
"""

import httpx
import pytest


@pytest.mark.e2e
def test_health_check(http_client: httpx.Client, backend_url: str):
    """Verify the backend health endpoint is reachable."""
    resp = http_client.get(f"{backend_url}/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.e2e
def test_full_research_flow(
    http_client: httpx.Client,
    backend_url: str,
    wait_for_task,
):
    """Submit a theme, wait for completion, and verify the report."""
    # 1. Submit a research task
    resp = http_client.post(
        f"{backend_url}/research",
        json={"theme": "Clean Energy"},
    )
    assert resp.status_code == 200
    data = resp.json()
    task_id = data["task_id"]
    assert data["status"] == "PENDING"

    # 2. Poll until the task completes (agent calls take time)
    final_status = wait_for_task(task_id, timeout=600)
    assert final_status == "SUCCESS"

    # 3. Retrieve the full report
    resp = http_client.get(f"{backend_url}/research/{task_id}/result")
    assert resp.status_code == 200
    result_data = resp.json()
    report = result_data["result"]

    # 4. Verify the report is a non-trivial Markdown document
    assert isinstance(report, str)
    assert len(report) > 500
    assert "#" in report  # Contains Markdown headings


@pytest.mark.e2e
def test_task_status_before_completion(
    http_client: httpx.Client,
    backend_url: str,
):
    """Verify that polling a newly submitted task returns a valid status."""
    resp = http_client.post(
        f"{backend_url}/research",
        json={"theme": "Quantum Computing"},
    )
    task_id = resp.json()["task_id"]

    resp = http_client.get(f"{backend_url}/research/{task_id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] in ("PENDING", "STARTED")


@pytest.mark.e2e
def test_result_before_completion_returns_error(
    http_client: httpx.Client,
    backend_url: str,
):
    """Verify that fetching result before completion returns 400."""
    resp = http_client.post(
        f"{backend_url}/research",
        json={"theme": "Agentic AI"},
    )
    task_id = resp.json()["task_id"]

    resp = http_client.get(f"{backend_url}/research/{task_id}/result")
    assert resp.status_code == 400

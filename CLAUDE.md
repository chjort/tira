# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

TIRA (Thematic Investment Research Agent) is an AI-powered platform that automatically
conducts institutional-quality thematic investment research (e.g., Quantum Computing,
Clean Energy, Agentic AI) and generates Markdown reports for portfolio managers.

**Status:** Core implementation complete. All five microservices are implemented and
orchestrated via Docker Compose.

## Tech Stack

- **Python 3.13**, managed with **uv** (not pip)
- **Docker Compose** for orchestrating all microservices
- **OpenAI Agent SDK** (`openai-agents`, imported as `agents`) for the research agent
- **Celery + Redis** for distributed task queue
- **FastAPI** for REST API backend
- **Streamlit** for frontend UI
- **MLFlow** for LLM tracing and observability
- **pytest** for testing (integration/e2e focus)

## Architecture

Five microservices, all deployed as Docker containers via `docker compose`:

1. **Research Agent Worker** — Celery worker running the OpenAI Agent SDK to produce
   Markdown research reports. Receives tasks via Redis.
2. **Task Queue Backend** — FastAPI app + Celery client. REST API for submitting
   research tasks, checking status, retrieving results.
3. **Task Queue Broker** — Redis instance (Celery message broker and result backend).
4. **Frontend** — Streamlit app for portfolio managers to submit themes and download
   reports.
5. **Tracing Server** — MLFlow instance for LLM call tracing and agent observability.

## Key Conventions

- Use `uv` for all Python dependency and environment management, never `pip` directly
- All agent code is async (`asyncio`-based)
- Reports are output as Markdown
- LLM and Agent tracing goes to MLFlow (using `mlflow.openai.autolog()`)
- LLM and Agent evaluation is performed using MLFlow
- Tests verify end-to-end research flow and cross-service integration
- Source-code for microservices is kept separate and each microservice is developed
  independently.
- Source-code always follow best-practices with modular code and docstrings.
- Python code should always be formatted with the Black formatter and imports sorted
  with Isort.

## Development notes

- Each microservice uses `src/` layout with hatchling
- Agent worker uses `--pool=threads` (not prefork) for asyncio compatibility
- The only coupling between backend and worker is the Celery task name string:
  `"agent_worker.tasks.run_research_task"` — defined in both `celery_client.py` and
  `tasks.py`. Never import agent_worker code from the backend.

## Commands

```bash
uv add <package>            # Add dependency
uv run <script.py>          # Run a script
uv run pytest               # Run tests
docker compose up           # Start all services
uvx ruff check              # Format with Black
uvx isort --sl --profile black  # Sort Python imports
```
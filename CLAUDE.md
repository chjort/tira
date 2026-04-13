# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TIRA (Thematic Investment Research Agent) is an AI-powered platform that automatically conducts institutional-quality thematic investment research (e.g., Quantum Computing, Clean Energy, Agentic AI) and generates Markdown reports for portfolio managers.

**Status:** Early development — architecture is designed, no application code written yet.

## Tech Stack

- **Python 3.13**, managed with **uv** (not pip)
- **Docker Compose** for orchestrating all microservices
- **OpenAI Agent SDK** (`openai-agents`, imported as `agents`) for the research agent
- **Celery + Redis** for distributed task queue
- **FastAPI** for REST API backend
- **Streamlit** for frontend UI
- **MLFlow** for LLM tracing and observability
- **pytest** for testing (integration/e2e focus)

## Commands

```bash
uv add <package>          # Add dependency
uv run <script.py>        # Run a script
uv run pytest             # Run tests
docker compose up         # Start all services
```

## Architecture

Five microservices, all deployed as Docker containers via `docker compose`:

1. **Research Agent Worker** — Celery worker running the OpenAI Agent SDK to produce Markdown research reports. Receives tasks via Redis.
2. **Task Queue Backend** — FastAPI app + Celery client. REST API for submitting research tasks, checking status, retrieving results.
3. **Task Queue Broker** — Redis instance (Celery message broker and result backend).
4. **Frontend** — Streamlit app for portfolio managers to submit themes and download reports.
5. **Tracing Server** — MLFlow instance for LLM call tracing and agent observability.

## Key Conventions

- Use `uv` for all Python dependency and environment management, never `pip` directly
- All agent code is async (`asyncio`-based)
- Reports are output as Markdown
- Tracing goes to MLFlow (disable openai-agents built-in tracing)
- Tests verify end-to-end research flow and cross-service integration

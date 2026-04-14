FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY src/ ./src/

CMD ["uv", "run", "uvicorn", "task_queue_backend.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]

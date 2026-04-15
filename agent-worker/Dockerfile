FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
RUN useradd --create-home worker && chown -R worker:worker /app
USER worker

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY src/ ./src/

CMD ["uv", "run", "celery", "-A", "agent_worker.celery_app", "worker", \
     "--loglevel=info", "--pool=threads", "--concurrency=4"]

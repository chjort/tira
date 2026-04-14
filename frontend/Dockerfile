FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY src/ ./src/

CMD ["uv", "run", "streamlit", "run", "src/frontend/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]

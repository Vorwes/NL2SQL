# syntax=docker/dockerfile:1

# Stage 1: Base Tooling
FROM python:3.12-slim AS uv-base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Stage 2A: Backend Builder
FROM uv-base AS backend-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project --group backend --no-group frontend
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --group backend --no-group frontend

# Stage 2B: Frontend Builder
FROM uv-base AS frontend-builder

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project --group frontend --no-group backend

COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --group frontend --no-group backend

# Stage 3A: Backend Runtime
FROM python:3.12-slim AS backend
ENV PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app"
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
RUN chown appuser:appuser /app

COPY --from=backend-builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser models/ ./models/
USER appuser
EXPOSE 8000
CMD ["python", "-m", "src.app.main"]

# Stage 3B: Frontend Runtime

FROM python:3.12-slim AS frontend
ENV PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app"
WORKDIR /app

RUN useradd -m appuser
RUN chown appuser:appuser /app

COPY --from=frontend-builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser src/app/user_interface.py ./src/app/
COPY --chown=appuser:appuser .chainlit/ ./.chainlit/
COPY --chown=appuser:appuser chainlit.md ./

USER appuser
EXPOSE 8001
CMD ["chainlit", "run", "src/app/user_interface.py", "--port", "8001", "--host", "0.0.0.0", "-h"]

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

RUN chown -R appuser:appgroup /app

RUN pip install --no-cache-dir uv

COPY --chown=appuser:appgroup . .

USER appuser

RUN uv sync --no-dev --frozen

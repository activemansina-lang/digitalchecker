FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run DB migrations then start the bot (long-polling process).
# `timeout 60` guarantees migrations never hang the container silently again —
# if they do, the process exits non-zero and Railway's restart policy kicks in
# with a clear "migration timed out" style log instead of eternal silence.
CMD ["sh", "-c", "timeout 60 alembic upgrade head && python -m app.main"]

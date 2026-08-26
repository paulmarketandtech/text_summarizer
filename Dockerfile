# syntax=docker/dockerfile:1

##########
# Builder
##########
FROM python:3.12-slim AS builder

# Copy uv binary (no curl install needed)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Faster + smaller installs
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Install dependencies only (good layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project --no-editable

# Copy project and install it (non-editable)
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

##########
# Runtime
##########
FROM python:3.12-slim

WORKDIR /app

# Only the runtime env vars you need
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8503 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_LOGGER_LEVEL=info

# Copy only the virtual environment (no uv binary)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create directories the app needs
RUN mkdir -p /app/archive/transcripts \
             /app/archive/summaries \
             /app/archive/logs \
             /app/data

EXPOSE 8503

# Run Streamlit directly from the venv (no `uv run`)
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8503"]

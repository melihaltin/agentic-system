# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (for building wheels if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Default environment
ENV PORT=8000 \
    ENV_FILE=.env

# Healthcheck (optional simple TCP check)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import socket,os; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1', int(os.getenv('PORT', '8000')))); s.close()" || exit 1

# Start the API
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

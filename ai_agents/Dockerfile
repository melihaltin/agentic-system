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

# Expose port for Flask webhook server
EXPOSE 5000

# Default environment
ENV PORT=5000 \
    AUDIO_STORAGE_PATH=/tmp/audio \
    ENV_FILE=.env

# Create audio storage path
RUN mkdir -p /tmp/audio

# Healthcheck for Flask server
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import socket,os; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1', int(os.getenv('PORT', '5000')))); s.close()" || exit 1

# Start the voice agent webhook server
CMD ["python", "voice_agent_main.py"]

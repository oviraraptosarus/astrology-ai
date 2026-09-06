FROM python:3.11-slim

# Metadata
LABEL org.opencontainers.image.title="astrology-ai" \
      org.opencontainers.image.description="Deterministic Vedic astrology engine + AI astrologer web app"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ASTRO_MODE=client_safe \
    PORT=8000

WORKDIR /app

# Build deps for C extensions (pyswisseph), then clean up in same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer-cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Application code
COPY . .

# Non-root runtime user; chart cache dir writable if used
RUN useradd --create-home --uid 10001 astro \
    && mkdir -p /app/cache \
    && chown -R astro:astro /app
USER astro

EXPOSE 8000

# Container-level healthcheck against the liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/health || exit 1

# Production process: uvicorn workers bound to 0.0.0.0, PORT from env
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout-keep-alive 75 --no-access-log"]

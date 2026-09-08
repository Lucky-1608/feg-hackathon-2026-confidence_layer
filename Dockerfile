# Stage 1: Build environment
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies from pyproject.toml
COPY pyproject.toml .
RUN mkdir -p src/confidence && touch src/confidence/__init__.py && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Stage 2: Runtime environment
FROM python:3.12-slim AS runner

WORKDIR /app

# Create non-root user
RUN groupadd -r confidence && useradd -r -g confidence -s /bin/false confidence

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source and project definition
COPY pyproject.toml .
COPY src/ ./src/
COPY demo/ ./demo/
COPY alembic/ ./alembic/
COPY alembic.ini .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src:/app:${PYTHONPATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install the application (non-editable)
RUN pip install --no-cache-dir --no-deps .

# Switch to non-root user
USER confidence

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "confidence.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

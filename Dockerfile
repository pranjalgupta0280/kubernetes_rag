# ============================================================
# FastAPI Backend Dockerfile
# Enterprise Agentic RAG
# ============================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (build-essential, git, libgomp1 for ML inference)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and data
COPY app/ ./app/
COPY processed_data/ ./processed_data/
COPY DATA/ ./DATA/

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/healthz || exit 1

# Launch FastAPI via Uvicorn
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2

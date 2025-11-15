# B4 Backend Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app

# Copy modules system
COPY backend/modules ./modules

# Optional: Copy world_model if it exists (for pipeline routes)
COPY world_model ./world_model 2>/dev/null || true

ENV PORT=8080 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    ENABLE_FIRESTORE_WRITES=true

EXPOSE 8080

# Run with uvicorn
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

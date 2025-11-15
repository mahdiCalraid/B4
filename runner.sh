#!/bin/bash

# Run the world model backend locally.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

echo "========================================================================"
echo "🚀 Starting World Model Backend Locally"
echo "========================================================================"

if [[ -f ".env" ]]; then
  echo "Loading environment variables from .env"
  set -a
  source ".env"
  set +a
else
  echo "No .env file found. Proceeding with default environment variables."
fi

export ENVIRONMENT="${ENVIRONMENT:-development}"
export PORT="${PORT:-8881}"
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-bthree-476203}"

# Ensure world_model sources are on PYTHONPATH for ad-hoc execution.
export PYTHONPATH="${ROOT_DIR}/world_model/src:${ROOT_DIR}:${PYTHONPATH:-}"

echo ""
echo "Configuration"
echo "  Environment : ${ENVIRONMENT}"
echo "  Port        : ${PORT}"
echo "  GCP Project : ${GOOGLE_CLOUD_PROJECT}"
echo "  Firestore   : ${ENABLE_FIRESTORE_WRITES:-false}"
echo ""
echo "Server will be available at http://localhost:${PORT}"
echo "Press Ctrl+C to stop."
echo "========================================================================"
echo ""

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT}" --reload

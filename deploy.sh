#!/bin/bash

# Build and deploy the world model backend to Cloud Run.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-bthree-476203}"
SERVICE_NAME="world-model-backend"
REGION="${REGION:-us-central1}"

echo "========================================"
echo "🚀 Deploying World Model Backend"
echo "========================================"
echo "Project : ${PROJECT_ID}"
echo "Service : ${SERVICE_NAME}"
echo "Region  : ${REGION}"
echo ""

gcloud config set project "${PROJECT_ID}"

echo "Submitting Cloud Build (this also deploys the service)..."
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project="${PROJECT_ID}"

echo ""
echo "Fetching service URL..."
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" --platform=managed --region="${REGION}" --format='value(status.url)')"

echo ""
echo "========================================"
echo "✅ Deployment complete"
echo "========================================"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Health check:"
curl -s "${SERVICE_URL}/health" || true
echo ""

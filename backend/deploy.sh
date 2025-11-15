#!/bin/bash

# B4 Backend Deployment Script
# Deploys to Google Cloud Run

set -e  # Exit on error

echo "🚀 B4 Backend Deployment"
echo "========================"
echo ""

# Check if we're in the backend directory
if [ ! -f "cloudbuild.yaml" ]; then
    echo "❌ Error: Must run from backend directory"
    echo "   cd /Users/ed/King/B4/backend && sh deploy.sh"
    exit 1
fi

# Get project ID from gcloud or use default
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project configured"
    echo "   Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo ""

# Confirm deployment
read -p "Deploy B4 backend to Cloud Run? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "🔨 Building and deploying..."
echo ""

# Change to project root for build context
cd ..

# Submit build to Cloud Build
gcloud builds submit \
    --config=backend/cloudbuild.yaml \
    --project=$PROJECT_ID

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Service URL:"
gcloud run services describe b4-backend \
    --region=us-central1 \
    --platform=managed \
    --format="value(status.url)" \
    --project=$PROJECT_ID

echo ""
echo "🔗 To set up Telegram webhook, use:"
echo "   SERVICE_URL=\$(gcloud run services describe b4-backend --region=us-central1 --platform=managed --format='value(status.url)')"
echo "   curl -X POST https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/setWebhook \\"
echo "        -d url=\"\${SERVICE_URL}/telegram/webhook\""
echo ""

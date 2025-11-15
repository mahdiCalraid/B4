# B4 Backend Deployment Guide

## Overview

This guide covers deploying the B4 backend to Google Cloud Run, identical to the working B3 deployment.

---

## Prerequisites

1. **Google Cloud Project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     containerregistry.googleapis.com \
     firestore.googleapis.com
   ```

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

---

## Quick Deployment

### One Command Deploy
```bash
cd /Users/ed/King/B4/backend
sh deploy.sh
```

This will:
1. Build Docker image using Cloud Build
2. Push to Container Registry
3. Deploy to Cloud Run (service name: `b4-backend`)
4. Display the service URL

---

## Manual Deployment Steps

### Step 1: Build Locally (Optional Test)
```bash
cd /Users/ed/King/B4

# Build Docker image
docker build -f backend/Dockerfile -t b4-backend .

# Test locally
docker run -p 8080:8080 \
  -e ENVIRONMENT=development \
  -e ENABLE_FIRESTORE_WRITES=false \
  b4-backend
```

### Step 2: Deploy to Cloud Run
```bash
cd /Users/ed/King/B4

# Submit to Cloud Build
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

This builds and deploys automatically!

### Step 3: Get Service URL
```bash
gcloud run services describe b4-backend \
  --region=us-central1 \
  --platform=managed \
  --format="value(status.url)"
```

---

## Configuration

### Environment Variables

Set via Cloud Run console or command:

```bash
gcloud run services update b4-backend \
  --region=us-central1 \
  --set-env-vars="KEY=VALUE"
```

**Available Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Environment name |
| `PORT` | `8080` | Server port |
| `ENABLE_FIRESTORE_WRITES` | `true` | Enable Firestore persistence |
| `GOOGLE_CLOUD_PROJECT` | Auto-set | GCP Project ID |
| `TELEGRAM_BOT_TOKEN` | - | Telegram bot token (if using webhooks) |
| `GEMINI_API_KEY` | - | Google Gemini API key (for AI modules) |
| `OPENAI_API_KEY` | - | OpenAI API key (for AI modules) |

### Set Secrets
```bash
# Store sensitive values in Secret Manager
echo -n "your-telegram-token" | \
  gcloud secrets create telegram-bot-token \
  --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding telegram-bot-token \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update service to use secret
gcloud run services update b4-backend \
  --region=us-central1 \
  --update-secrets=TELEGRAM_BOT_TOKEN=telegram-bot-token:latest
```

---

## Telegram Webhook Setup

Once deployed, connect Telegram:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe b4-backend \
  --region=us-central1 \
  --platform=managed \
  --format="value(status.url)")

# Set Telegram webhook
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -d url="${SERVICE_URL}/telegram/webhook"

# Verify webhook
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo
```

---

## Monitoring & Logs

### View Logs
```bash
# Stream logs
gcloud run logs tail b4-backend --region=us-central1

# View in Cloud Console
gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)"
```

### Check Service Status
```bash
# Service details
gcloud run services describe b4-backend --region=us-central1

# List all revisions
gcloud run revisions list \
  --service=b4-backend \
  --region=us-central1
```

### Metrics
View in Cloud Console:
- Requests per second
- Latency (p50, p95, p99)
- Error rate
- Instance count

---

## Scaling Configuration

### Auto-scaling
```bash
gcloud run services update b4-backend \
  --region=us-central1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=80
```

### Resource Limits
```bash
gcloud run services update b4-backend \
  --region=us-central1 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300
```

---

## Update Deployment

### Deploy New Version
```bash
# Just run deploy script again
cd /Users/ed/King/B4/backend
sh deploy.sh
```

### Rollback to Previous Version
```bash
# List revisions
gcloud run revisions list \
  --service=b4-backend \
  --region=us-central1

# Rollback
gcloud run services update-traffic b4-backend \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

---

## Testing Deployed Service

### Test Module Endpoint
```bash
SERVICE_URL=$(gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)")

# Test service
curl $SERVICE_URL/

# Test chat
curl -X POST $SERVICE_URL/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Cloud Run!"}'

# Test analyzer
curl -X POST $SERVICE_URL/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge to $100/barrel"}'
```

---

## Cost Optimization

### Current Configuration
- **Memory**: 512Mi
- **CPU**: 1
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10
- **Timeout**: 300s

### Estimated Costs
Based on us-central1 pricing:
- **Idle**: $0/month (scales to zero)
- **Light usage** (100 req/day): ~$1-2/month
- **Moderate usage** (1000 req/day): ~$5-10/month

### Reduce Costs
```bash
# Reduce memory
gcloud run services update b4-backend \
  --region=us-central1 \
  --memory=256Mi

# Reduce timeout
gcloud run services update b4-backend \
  --region=us-central1 \
  --timeout=60
```

---

## Troubleshooting

### Deployment Fails

**Check build logs:**
```bash
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

**Common issues:**
- Missing files in Dockerfile COPY commands
- Python dependency conflicts
- Insufficient permissions

### Service Not Responding

**Check logs:**
```bash
gcloud run logs tail b4-backend --region=us-central1
```

**Common issues:**
- Module import errors
- Missing environment variables
- Port binding issues (must use $PORT)

### Telegram Webhook Not Working

**Check webhook status:**
```bash
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo
```

**Common issues:**
- Incorrect webhook URL
- Service not allowing unauthenticated requests
- SSL certificate issues

---

## Production Checklist

Before going live:

- [ ] Set all required environment variables
- [ ] Store secrets in Secret Manager
- [ ] Configure appropriate scaling limits
- [ ] Set up monitoring and alerting
- [ ] Test all module endpoints
- [ ] Test Telegram webhook (if using)
- [ ] Configure custom domain (optional)
- [ ] Set up Cloud Armor for DDoS protection (optional)
- [ ] Configure VPC connector (optional)
- [ ] Review and set budget alerts

---

## Comparison with B3

| Feature | B3 | B4 |
|---------|----|----|
| Service name | `b3` | `b4-backend` |
| Module system | ❌ | ✅ |
| Telegram | ✅ | ✅ (compatible) |
| Auto-routing | ❌ | ✅ |
| Documentation | ✅ | ✅ Enhanced |
| Deployment | ✅ | ✅ Same process |

**B4 is a drop-in replacement for B3 with added module functionality!**

---

## Quick Reference

```bash
# Deploy
cd /Users/ed/King/B4/backend && sh deploy.sh

# View logs
gcloud run logs tail b4-backend --region=us-central1

# Get URL
gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)"

# Update environment
gcloud run services update b4-backend \
  --region=us-central1 \
  --set-env-vars="KEY=VALUE"

# Rollback
gcloud run revisions list --service=b4-backend --region=us-central1
gcloud run services update-traffic b4-backend \
  --to-revisions=REVISION=100 \
  --region=us-central1
```

---

**Version**: 1.0
**Last Updated**: November 10, 2025
**Compatible with**: B3 infrastructure
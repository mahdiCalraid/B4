# B4 Backend - Deployment Ready! 🚀

## Complete Setup: Local + Cloud

Your B4 backend is now ready for **both local development** and **Cloud Run deployment** (just like B3).

---

## Local Development

### Start Server
```bash
cd /Users/ed/King/B4/backend
sh run.sh
```

### Test Locally
```bash
curl http://localhost:8080/
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
```

### Stop Server
```bash
sh stop.sh
# or press Ctrl+C
```

---

## Cloud Deployment (Same as B3)

### One-Command Deploy
```bash
cd /Users/ed/King/B4/backend
sh deploy.sh
```

This will:
1. ✅ Build Docker image using Cloud Build
2. ✅ Push to Container Registry
3. ✅ Deploy to Cloud Run as `b4-backend`
4. ✅ Display service URL

### Service Name
- **B3**: `b3`
- **B4**: `b4-backend`

Both can run simultaneously!

---

## What's Included

### ✅ Files Created/Updated:

| File | Purpose |
|------|---------|
| `backend/Dockerfile` | Container image definition |
| `backend/cloudbuild.yaml` | Cloud Build configuration |
| `backend/deploy.sh` | One-command deployment |
| `backend/DEPLOYMENT.md` | Complete deployment guide |
| `backend/.dockerignore` | Docker build optimization |
| `backend/.gcloudignore` | Cloud Build optimization |
| `backend/run.sh` | Local development |
| `backend/stop.sh` | Stop local server |

---

## Deployment Process

### Prerequisites (One-Time Setup)

```bash
# Set GCP project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  firestore.googleapis.com

# Authenticate
gcloud auth login
gcloud auth application-default login
```

### Deploy

```bash
cd /Users/ed/King/B4/backend
sh deploy.sh
```

**Deployment takes 3-5 minutes.**

---

## After Deployment

### Get Service URL
```bash
gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)"
```

### Test Deployed Service
```bash
SERVICE_URL=$(gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)")

# Test service
curl $SERVICE_URL/

# Test chat
curl -X POST $SERVICE_URL/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Cloud!"}'
```

### Set Up Telegram Webhook
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)")

# Set webhook
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -d url="${SERVICE_URL}/telegram/webhook"
```

---

## Configuration

### Environment Variables

Set via Cloud Run:

```bash
gcloud run services update b4-backend \
  --region=us-central1 \
  --set-env-vars="TELEGRAM_BOT_TOKEN=your-token,GEMINI_API_KEY=your-key"
```

**Available Variables:**
- `ENVIRONMENT` - `production`
- `PORT` - `8080` (auto-set)
- `ENABLE_FIRESTORE_WRITES` - `true`
- `GOOGLE_CLOUD_PROJECT` - auto-set
- `TELEGRAM_BOT_TOKEN` - Your bot token
- `GEMINI_API_KEY` - For AI modules
- `OPENAI_API_KEY` - For AI modules

---

## Module System

Both local and deployed versions include:

✅ **ChatAgentModule** - Conversational AI
✅ **AnalyzerModule** - Text analysis
✅ **Module Registry** - Auto-discovery
✅ **Intelligent Router** - Auto-routing
✅ **REST API** - `/api/modules/*`

Add more modules by editing `app/startup.py`!

---

## Monitoring

### View Logs
```bash
# Stream logs
gcloud run logs tail b4-backend --region=us-central1

# View specific errors
gcloud run logs read b4-backend \
  --region=us-central1 \
  --filter="severity>=ERROR"
```

### Check Service Status
```bash
gcloud run services describe b4-backend --region=us-central1
```

### Metrics
View in Cloud Console:
- Request rate
- Latency
- Error rate
- Instance count

---

## Cost

### Pricing (us-central1)
- **Idle**: $0/month (scales to zero)
- **Light usage** (100 req/day): ~$1-2/month
- **Moderate** (1000 req/day): ~$5-10/month

### Current Configuration
- Memory: 512Mi
- CPU: 1
- Min instances: 0
- Max instances: 10
- Timeout: 300s

---

## Comparison: B3 vs B4

| Feature | B3 | B4 |
|---------|----|----|
| **Service name** | `b3` | `b4-backend` |
| **Telegram** | ✅ | ✅ Same setup |
| **Module system** | ❌ | ✅ New! |
| **Auto-routing** | ❌ | ✅ New! |
| **REST API** | ✅ | ✅ Enhanced |
| **Deployment** | ✅ | ✅ Same process |
| **Cost** | ~$2-5/mo | ~$2-5/mo |

**B4 is fully compatible with B3 infrastructure!**

---

## Quick Command Reference

### Local Development
```bash
# Start
cd /Users/ed/King/B4/backend && sh run.sh

# Stop
sh stop.sh

# Test
curl http://localhost:8080/
```

### Cloud Deployment
```bash
# Deploy
cd /Users/ed/King/B4/backend && sh deploy.sh

# Get URL
gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)"

# View logs
gcloud run logs tail b4-backend --region=us-central1

# Update env vars
gcloud run services update b4-backend \
  --region=us-central1 \
  --set-env-vars="KEY=VALUE"
```

---

## Documentation

- **`START_HERE.md`** - Quick start
- **`COMMANDS.md`** - All commands
- **`backend/README.md`** - Complete guide
- **`backend/DEPLOYMENT.md`** - Deployment details (detailed!)
- **`backend/QUICKSTART.md`** - Quick reference

---

## What You Can Do Now

### 1. Test Locally
```bash
cd /Users/ed/King/B4/backend
sh run.sh
# Test with Postman or cURL
```

### 2. Deploy to Cloud
```bash
cd /Users/ed/King/B4/backend
sh deploy.sh
# Takes 3-5 minutes
```

### 3. Connect Telegram
```bash
# After deployment
SERVICE_URL=$(gcloud run services describe b4-backend \
  --region=us-central1 \
  --format="value(status.url)")

curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -d url="${SERVICE_URL}/telegram/webhook"
```

### 4. Both B3 and B4 Can Run Together!
- **B3**: `b3.us-central1.run.app`
- **B4**: `b4-backend.us-central1.run.app`

---

## Summary

✅ **Local development**: `sh run.sh`
✅ **Cloud deployment**: `sh deploy.sh`
✅ **Same process as B3**: Proven and working
✅ **Module system**: New and enhanced
✅ **Telegram compatible**: Works like B3
✅ **Fully documented**: Complete guides

**Everything is ready!** 🎉

---

**Version**: 1.0
**Date**: November 10, 2025
**Status**: ✅ READY FOR LOCAL + CLOUD
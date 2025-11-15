# B4 Backend - Command Reference

## Starting & Stopping

### Start Server
```bash
cd /Users/ed/King/B4/backend
sh run.sh
```

### Stop Server
**Option 1: Ctrl+C** (in the terminal running the server)

**Option 2: Kill script**
```bash
cd /Users/ed/King/B4/backend
sh stop.sh
```

**Option 3: Manual**
```bash
lsof -ti:8080 | xargs kill -9
```

---

## Testing Commands

### Check Service
```bash
curl http://localhost:8080/
```

**Expected Output:**
```json
{
  "service": "world-model-backend",
  "status": "running",
  "modules_loaded": 2,
  "endpoints": {
    "health": "/health",
    "modules": "/api/modules/",
    "chat": "/api/modules/chat"
  }
}
```

### List All Modules
```bash
curl http://localhost:8080/api/modules/
```

### Get Module Info
```bash
curl http://localhost:8080/api/modules/ChatAgentModule
```

---

## Chat Module Examples

### Simple Greeting
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
```

### Ask for Help
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What can you help me with?"}'
```

### Request Analysis
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Please analyze the oil market"}'
```

---

## Analyzer Module Examples

### Analyze News Article
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Oil prices surge to $100/barrel amid supply concerns and geopolitical tensions. Markets react negatively to the news."
  }'
```

### Analyze with Details
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "President announces new economic policy to combat inflation",
    "params": {"include_details": true}
  }'
```

### Analyze Tech News
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "New AI breakthrough announced by leading tech company. Revolutionary machine learning algorithms outperform previous models."
  }'
```

---

## Formatted Output (with jq)

If you have `jq` installed, you can format the JSON output:

```bash
# Pretty print service info
curl http://localhost:8080/ | jq

# Get just the module count
curl http://localhost:8080/ | jq '.modules_loaded'

# Get module names
curl http://localhost:8080/api/modules/ | jq '.modules | keys'

# Get chat response
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}' | jq '.response'

# Get analysis topics
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge"}' | jq '.analysis.topics'
```

---

## Debugging Commands

### Check if Server is Running
```bash
lsof -i:8080
```

### Check Server Logs
Logs appear in the terminal where you ran `sh run.sh`

### Test with Verbose Output
```bash
curl -v http://localhost:8080/
```

### Check Python Virtual Environment
```bash
cd /Users/ed/King/B4/backend
source venv/bin/activate
which python  # Should show: /Users/ed/King/B4/backend/venv/bin/python
```

---

## Postman Testing

### Import Collection
1. Open Postman
2. Import → File → Select `B4_Postman_Collection.json`
3. Set environment variable `base_url` = `http://localhost:8080`
4. Run requests

### Available Requests
- Service Info
- Health Check
- List All Modules
- Get Module Info
- Chat - Hello
- Chat - Help
- Chat - Request Analysis
- Analyze - Oil Market
- Analyze - Tech News
- Analyze - Political News

---

## Browser Testing

### Interactive API Documentation
```
http://localhost:8080/docs
```

Features:
- Browse all endpoints
- Try out requests directly
- See request/response schemas
- No coding required!

---

## Development Commands

### Reinstall Dependencies
```bash
cd /Users/ed/King/B4/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Check Installed Packages
```bash
cd /Users/ed/King/B4/backend
source venv/bin/activate
pip list
```

### Run with Debug Mode
```bash
cd /Users/ed/King/B4/backend
source venv/bin/activate
./venv/bin/python -m app.main --reload
```

---

## Common Workflows

### Quick Test Workflow
```bash
# 1. Start server
cd /Users/ed/King/B4/backend && sh run.sh

# 2. In another terminal, test
curl http://localhost:8080/
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'

# 3. Stop server
sh stop.sh  # or Ctrl+C
```

### Development Workflow
```bash
# 1. Make changes to module code
# 2. Server auto-reloads (if running)
# 3. Test changes immediately
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

---

## Troubleshooting

### Port Already in Use
```bash
cd /Users/ed/King/B4/backend
sh stop.sh
sh run.sh
```

### Module Not Loading
Check server startup logs for errors:
```
✅ Total modules registered: 2
```

If less than 2, check `app/startup.py` for import errors.

### Connection Refused
Make sure server is running:
```bash
lsof -i:8080
```

If nothing shows, start the server.

---

**Quick Reference:**

| Command | Purpose |
|---------|---------|
| `sh run.sh` | Start server |
| `sh stop.sh` | Stop server |
| `curl http://localhost:8080/` | Check service |
| `curl http://localhost:8080/api/modules/` | List modules |
| `open http://localhost:8080/docs` | Open API docs |

---

**Version**: 1.0
**Last Updated**: November 10, 2025
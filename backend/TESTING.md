# B4 Backend Testing Guide

## Quick Test Commands

### 1. Start the Server
```bash
cd /Users/ed/King/B4/backend
sh run.sh
```

Wait for the message: `✅ Total modules registered: 2`

### 2. Test Service (Should see module count)
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

### 3. List Modules
```bash
curl http://localhost:8080/api/modules/ | jq
```

**Expected Output:**
```json
{
  "count": 2,
  "modules": {
    "ChatAgentModule": {...},
    "AnalyzerModule": {...}
  }
}
```

### 4. Test Chat Module
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "user_id": "test"}' | jq
```

**Expected Output:**
```json
{
  "response": "Hello! How can I help you today?",
  "confidence": 0.85,
  "intent": "greeting",
  "processing_time_ms": 12,
  "module": "ChatAgentModule"
}
```

### 5. Test Analyzer Module
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge to $100/barrel"}' | jq
```

**Expected Output:**
```json
{
  "analysis": {
    "keywords": ["prices", "surge", "barrel"],
    "entities": ["Oil", "$100", "barrel"],
    "sentiment": {
      "label": "negative",
      "score": 0.4
    },
    "topics": ["energy", "markets"]
  },
  "confidence": 0.92,
  "processing_time_ms": 45
}
```

## Test Scenarios

### Scenario 1: Auto-routing to Chat
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hi, how are you?"}' | jq '.module'
```

Should return: `"ChatAgentModule"`

### Scenario 2: Auto-routing to Analyzer
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Please analyze this text"}' | jq '.module'
```

Should return: `"ChatAgentModule"` (routes to help message about AnalyzerModule)

### Scenario 3: Direct Module Call
```bash
curl -X POST http://localhost:8080/api/modules/ChatAgentModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Direct call"}' | jq
```

Should process successfully.

### Scenario 4: Module Not Found
```bash
curl -X POST http://localhost:8080/api/modules/NonExistentModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

Should return HTTP 404 with error message.

## Validation Checklist

- [ ] Server starts without errors
- [ ] 2 modules registered on startup
- [ ] Root endpoint shows `modules_loaded: 2`
- [ ] `/api/modules/` lists ChatAgentModule and AnalyzerModule
- [ ] Chat endpoint responds to "Hello"
- [ ] Analyzer extracts keywords correctly
- [ ] Auto-routing works based on content
- [ ] Direct module calls work
- [ ] Invalid module returns 404
- [ ] API docs accessible at `/docs`

## Common Issues

### Issue: Module not registered
**Symptom**: `modules_loaded: 0` or specific module missing

**Solution**:
1. Check `app/startup.py` for import errors
2. Restart server: `Ctrl+C` then `sh run.sh`
3. Check console for error messages

### Issue: ImportError
**Symptom**: `Could not import ChatAgentModule`

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Issue: Port in use
**Symptom**: `Address already in use`

**Solution**:
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use different port
export PORT=8081
sh run.sh
```

## Performance Tests

### Response Time Test
```bash
time curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

Should complete in < 1 second.

### Concurrent Requests Test
```bash
# Send 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8080/api/modules/chat \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"test $i\"}" &
done
wait
```

All should complete successfully.

## Next Steps After Successful Tests

1. Add more sophisticated modules (with AI)
2. Add module-specific configuration
3. Add authentication
4. Add rate limiting
5. Add database persistence
6. Add background workers

---

**Last Updated**: November 10, 2025
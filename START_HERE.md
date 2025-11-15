# B4 Backend - START HERE 🚀

## What We Built

A **complete FastAPI backend** with modular architecture. No Telegram integration needed - test everything via REST API!

## Quick Start (2 Commands!)

```bash
# 1. Start the server
cd /Users/ed/King/B4/backend && sh run.sh

# 2. Test it works (in another terminal)
curl http://localhost:8080/
```

That's it! Server is running on **`http://localhost:8080`**

---

## Test the Modules

### Test Chat Module
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! How are you?"}'
```

### Test Analyzer Module
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge to $100/barrel amid supply concerns"}'
```

### List All Modules
```bash
curl http://localhost:8080/api/modules/
```

---

## View API Documentation

Open in browser: **`http://localhost:8080/docs`**

Interactive API documentation with "Try it out" buttons!

---

## What's Available

### 2 Working Modules:

1. **ChatAgentModule** - Conversational AI
   - Handles greetings
   - Provides help
   - Routes to specialized modules

2. **AnalyzerModule** - Text Analysis
   - Keyword extraction
   - Entity recognition
   - Sentiment analysis
   - Topic classification

### API Endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Service info (shows modules_loaded: 2) |
| `GET /health` | Health check |
| `GET /api/modules/` | List all modules |
| `POST /api/modules/chat` | Chat (auto-routes to best module) |
| `POST /api/modules/{name}/process` | Call specific module |
| `GET /docs` | Interactive API docs |

---

## Architecture

```
Request → FastAPI → Router → Module → Response
```

- **Backend**: Routes requests (no business logic)
- **Modules**: All processing logic (completely independent)
- **Router**: Intelligently determines which module to use

---

## Complete Documentation

- **This File**: Quick start
- `backend/QUICKSTART.md`: Quick reference
- `backend/README.md`: Complete guide
- `backend/TESTING.md`: Testing scenarios
- `docs/IMPLEMENTATION_COMPLETE_PHASE1.md`: What we built
- `docs/B4_BACKEND_ARCHITECTURE.md`: Architecture details

---

## Troubleshooting

### Server won't start?
```bash
# Make sure you're in the backend directory
cd /Users/ed/King/B4/backend

# Run the script
sh run.sh
```

### Port already in use?
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Then start again
sh run.sh
```

### Want to see what's happening?
Check the terminal where you ran `sh run.sh` - all logs appear there.

---

## Next Steps

Once you verify everything works:

1. Add AI integration (Gemini/OpenAI) to modules
2. Add more sophisticated modules
3. Add background workers
4. Add Firestore persistence
5. Add Telegram webhook (you already tested this separately)

---

## Example Session

```bash
# Terminal 1: Start server
$ cd /Users/ed/King/B4/backend
$ sh run.sh
🚀 Starting B4 Backend...
📦 Creating virtual environment...
🔧 Activating virtual environment...
📥 Installing dependencies...
✅ Starting server on http://localhost:8080
...
✅ Total modules registered: 2

# Terminal 2: Test it
$ curl http://localhost:8080/
{
  "service": "world-model-backend",
  "status": "running",
  "modules_loaded": 2,
  ...
}

$ curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
{
  "response": "Hello! How can I help you today?",
  "confidence": 0.85,
  ...
}
```

---

## That's It!

Everything is ready to go. Just run:

```bash
cd /Users/ed/King/B4/backend && sh run.sh
```

Then test with cURL, Postman, or browser at `http://localhost:8080/docs`

---

**Version**: 1.0
**Status**: ✅ READY TO USE
**Last Updated**: November 10, 2025
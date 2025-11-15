# B4 Backend - Quick Start

## Run the Backend

```bash
cd /Users/ed/King/B4/backend
sh run.sh
```

Wait for message: `✅ Total modules registered: 2`

## Test It Works

### In another terminal:

```bash
# Test service (should show modules_loaded: 2)
curl http://localhost:8080/

# Test chat
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'

# Test analyzer
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge to $100/barrel"}'
```

## View API Documentation

Open in browser: `http://localhost:8080/docs`

## Stop Server

Press `Ctrl+C` in the terminal running the server

---

That's it! See [README.md](README.md) for complete documentation.
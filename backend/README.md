# B4 Backend - Module System

FastAPI backend with pluggable module architecture for processing various types of requests.

## Quick Start

```bash
cd /Users/ed/King/B4/backend
sh run.sh
```

The server will start on `http://localhost:8080`

## Architecture

```
Request → FastAPI → Router → Module → Response
```

- **FastAPI**: HTTP server and routing
- **Router**: Intelligently routes requests to appropriate modules
- **Modules**: Self-contained processing units (chat, analysis, etc.)

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── startup.py           # Module registration
│   ├── routes/
│   │   ├── modules.py       # Module API endpoints
│   │   └── pipeline.py      # (existing) Pipeline endpoints
│   └── services/            # (existing) Services
│
└── modules/
    ├── base.py              # BaseModule interface
    ├── registry.py          # Module registry
    ├── router.py            # Intelligent routing
    │
    └── interactive/         # User-facing modules
        ├── chat_agent/      # Conversational AI
        │   └── module.py
        └── analyzer/        # Text analysis
            └── module.py
```

## API Endpoints

### 1. Service Info
```bash
GET http://localhost:8080/
```

Returns service metadata and available endpoints.

### 2. List Modules
```bash
GET http://localhost:8080/api/modules/
```

Returns all registered modules.

**Example Response:**
```json
{
  "count": 2,
  "modules": {
    "ChatAgentModule": {
      "name": "ChatAgentModule",
      "type": "interactive",
      "version": "1.0.0",
      "description": "Simple conversational AI agent."
    },
    "AnalyzerModule": {
      "name": "AnalyzerModule",
      "type": "interactive",
      "version": "1.0.0",
      "description": "Analyzes text and extracts insights..."
    }
  }
}
```

### 3. Chat (Auto-routing)
```bash
POST http://localhost:8080/api/modules/chat
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "user_id": "user123"
}
```

Automatically routes to the appropriate module based on content.

**Example Response:**
```json
{
  "response": "Hello! How can I help you today?",
  "confidence": 0.85,
  "intent": "greeting",
  "processing_time_ms": 12,
  "module": "ChatAgentModule",
  "timestamp": "2025-11-10T12:00:00"
}
```

### 4. Analyze Text
```bash
POST http://localhost:8080/api/modules/AnalyzerModule/process
Content-Type: application/json

{
  "text": "Oil prices surge to $100/barrel amid supply concerns",
  "params": {
    "include_details": true
  }
}
```

**Example Response:**
```json
{
  "analysis": {
    "keywords": ["prices", "surge", "barrel", "supply", "concerns"],
    "entities": ["Oil", "$100", "barrel"],
    "sentiment": {
      "label": "negative",
      "score": 0.4,
      "positive_signals": 1,
      "negative_signals": 2
    },
    "topics": ["energy", "markets"],
    "statistics": {
      "words": 8,
      "characters": 51,
      "sentences": 1,
      "paragraphs": 1
    }
  },
  "confidence": 0.92,
  "processing_time_ms": 45,
  "module": "AnalyzerModule"
}
```

### 5. Call Specific Module
```bash
POST http://localhost:8080/api/modules/ChatAgentModule/process
Content-Type: application/json

{
  "text": "What can you do?",
  "user_id": "test_user"
}
```

## Testing with cURL

### Test Service
```bash
curl http://localhost:8080/
```

### List Modules
```bash
curl http://localhost:8080/api/modules/
```

### Chat
```bash
curl -X POST http://localhost:8080/api/modules/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "user_id": "test"}'
```

### Analyze
```bash
curl -X POST http://localhost:8080/api/modules/AnalyzerModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Oil prices surge to $100 amid supply concerns"}'
```

## Testing with Postman

1. Import the collection (see `postman_collection.json`)
2. Set environment variable `base_url` to `http://localhost:8080`
3. Run the requests

## Adding New Modules

### 1. Create Module Directory
```bash
mkdir -p modules/interactive/my_module
cd modules/interactive/my_module
touch __init__.py module.py
```

### 2. Implement Module Class

```python
# modules/interactive/my_module/module.py

from typing import Dict, Any
from datetime import datetime
from modules.base import BaseModule, ModuleType


class MyModule(BaseModule):
    """
    Description of what your module does.
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.INTERACTIVE
        self.version = "1.0.0"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the request."""
        start_time = datetime.now()

        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {"error": error, "confidence": 0.0}

        # Your processing logic here
        text = input_data.get("text", "")
        result = f"Processed: {text}"

        return {
            "response": result,
            "confidence": 0.9,
            **self._get_processing_metadata(start_time)
        }
```

### 3. Register Module

Add to `app/startup.py`:

```python
from modules.interactive.my_module.module import MyModule
registry.register(MyModule)
```

### 4. Restart Server

```bash
# Press Ctrl+C to stop
sh run.sh
```

Your module is now available!

## Module Types

### Interactive Modules
- Respond to user requests immediately
- Example: ChatAgent, Analyzer
- Located in `modules/interactive/`

### Background Workers (Future)
- Run autonomously on schedule
- Example: NewsScraper, EventMonitor
- Located in `modules/background/`

### External Connectors (Future)
- Interact with external APIs
- Example: TradingAPI, MarketData
- Located in `modules/connectors/`

## Environment Variables

Create a `.env` file in the backend directory:

```bash
# Development mode
ENVIRONMENT=development

# Server port
PORT=8080

# Firestore (optional, for persistence)
ENABLE_FIRESTORE_WRITES=False
GOOGLE_CLOUD_PROJECT=your-project-id

# AI API Keys (for modules that use them)
# GEMINI_API_KEY=your-key
# OPENAI_API_KEY=your-key
```

## Development

### Run with Auto-reload
```bash
python -m app.main
```

The server will automatically reload when you change Python files.

### View API Documentation
```bash
open http://localhost:8080/docs
```

FastAPI automatically generates interactive API documentation.

### Check Module Status
```bash
curl http://localhost:8080/api/modules/ChatAgentModule
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use a different port
export PORT=8081
sh run.sh
```

### Module Not Found
- Check that module is imported in `app/startup.py`
- Restart the server to trigger module registration
- Check for import errors in console output

### Import Errors
- Ensure virtual environment is activated
- Install requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

## Next Steps

1. ✅ **Basic system working**
2. Add more sophisticated modules (with AI)
3. Add background workers with Celery
4. Add Firestore persistence
5. Add authentication
6. Add webhook support (Telegram, WhatsApp)

## API Documentation

Visit `http://localhost:8080/docs` for full interactive API documentation.

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
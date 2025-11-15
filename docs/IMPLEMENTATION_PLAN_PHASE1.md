# B4 Implementation Plan - Phase 1: Core Backend & Modules

**Version**: 1.0
**Date**: November 10, 2025
**Status**: In Progress

---

## Phase 1 Scope

**Goal**: Build the core Django backend with module system, testable via REST API and Postman.

**Excluded for Now**:
- ❌ Telegram/WhatsApp webhooks (already tested separately)
- ❌ Background workers (Celery)
- ❌ Event processing pipeline
- ❌ Database integrations (Firestore/PostgreSQL)

**Included in Phase 1**:
- ✅ Django project setup
- ✅ Base module interface
- ✅ Module registry & router
- ✅ REST API endpoints for testing
- ✅ Simple in-memory storage
- ✅ 2-3 example modules (ChatAgent, Analyzer)
- ✅ Complete Postman collection

---

## Deliverables Checklist

### 1. Django Project Structure ✅
```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── api/           # REST API
│   ├── modules/       # Module management
│   └── core/          # Shared utilities
│
└── modules/
    ├── base.py
    ├── interactive/
    │   ├── chat_agent/
    │   └── analyzer/
    └── background/
        └── example/
```

### 2. Base Module System ✅
- `BaseModule` abstract class
- `ModuleType` enum
- Input/output validation
- Health check interface

### 3. Module Registry ✅
- Auto-discovery on startup
- Module registration
- Get module by name
- List available modules

### 4. Module Router ✅
- Pattern-based routing
- Explicit module selection
- Error handling

### 5. REST API ✅
- `POST /api/chat` - Send message to any module
- `GET /api/modules` - List available modules
- `POST /api/modules/{name}/process` - Call specific module
- `GET /api/health` - Health check

### 6. Example Modules ✅
- **ChatAgentModule**: Simple conversational AI
- **AnalyzerModule**: Analyzes text and returns insights

### 7. Testing Tools ✅
- Postman collection
- Sample requests
- Documentation

---

## Implementation Steps

### Step 1: Initialize Django Project
```bash
cd backend
django-admin startproject config .
python manage.py startapp api
python manage.py startapp modules_app
python manage.py startapp core
```

### Step 2: Install Dependencies
```bash
pip install django djangorestframework python-dotenv
pip freeze > requirements.txt
```

### Step 3: Configure Settings
- Set up environment variables
- Configure ALLOWED_HOSTS
- Add apps to INSTALLED_APPS
- Configure REST framework

### Step 4: Implement Base Module
```python
# modules/base.py
class BaseModule(ABC):
    @abstractmethod
    async def process(self, input_data: Dict) -> Dict:
        pass
```

### Step 5: Implement Module Registry
```python
# apps/modules_app/registry.py
class ModuleRegistry:
    def register(self, module_class): ...
    def get_module(self, name): ...
```

### Step 6: Create Example Modules
- ChatAgentModule with simple AI
- AnalyzerModule with pattern matching

### Step 7: Build REST API
- ViewSets for module operations
- Serializers for request/response
- URL routing

### Step 8: Test with Postman
- Create collection
- Test all endpoints
- Document responses

---

## File Structure Details

### Backend Root
```
backend/
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .env                      # Actual environment (gitignored)
├── README.md                 # Setup instructions
└── .gitignore               # Git ignore rules
```

### Config Package (Django Settings)
```
config/
├── __init__.py
├── settings.py               # Main settings
├── urls.py                   # Root URL routing
├── wsgi.py                   # WSGI config
└── asgi.py                   # ASGI config
```

### Apps Package
```
apps/
├── __init__.py
│
├── api/                      # REST API
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py             # API endpoints
│   ├── serializers.py       # Request/response models
│   ├── urls.py              # API URL routing
│   └── permissions.py       # (Future: auth)
│
├── modules_app/              # Module management
│   ├── __init__.py
│   ├── apps.py              # Auto-discovery happens here
│   ├── registry.py          # ModuleRegistry
│   ├── router.py            # ModuleRouter
│   └── models.py            # (Future: DB models)
│
└── core/                     # Shared utilities
    ├── __init__.py
    ├── exceptions.py        # Custom exceptions
    ├── logging.py           # Logging setup
    └── utils.py             # Helper functions
```

### Modules Package
```
modules/
├── __init__.py
├── base.py                   # BaseModule interface
│
├── interactive/              # User-facing modules
│   ├── __init__.py
│   │
│   ├── chat_agent/
│   │   ├── __init__.py
│   │   ├── module.py        # ChatAgentModule
│   │   ├── agent.py         # Agent logic
│   │   └── README.md        # Module docs
│   │
│   └── analyzer/
│       ├── __init__.py
│       ├── module.py        # AnalyzerModule
│       ├── analyzer.py      # Analysis logic
│       └── README.md
│
└── background/               # Background workers (future)
    ├── __init__.py
    └── example/
        ├── __init__.py
        ├── module.py
        └── README.md
```

---

## API Endpoints Specification

### 1. Health Check
```
GET /api/health

Response:
{
    "status": "healthy",
    "timestamp": "2025-11-10T12:00:00Z",
    "modules_loaded": 2
}
```

### 2. List Modules
```
GET /api/modules

Response:
{
    "modules": [
        {
            "name": "ChatAgentModule",
            "type": "interactive",
            "version": "1.0.0",
            "description": "Simple conversational AI agent"
        },
        {
            "name": "AnalyzerModule",
            "type": "interactive",
            "version": "1.0.0",
            "description": "Analyzes text and returns insights"
        }
    ]
}
```

### 3. Process Message (Auto-route)
```
POST /api/chat
Content-Type: application/json

{
    "text": "What is the weather like?",
    "user_id": "user123"
}

Response:
{
    "module_used": "ChatAgentModule",
    "response": "I'm a simple chatbot. I can help you with basic questions.",
    "confidence": 0.85,
    "processing_time_ms": 123
}
```

### 4. Call Specific Module
```
POST /api/modules/AnalyzerModule/process
Content-Type: application/json

{
    "text": "Oil prices surge to $100/barrel amid supply concerns",
    "params": {
        "include_sentiment": true
    }
}

Response:
{
    "module": "AnalyzerModule",
    "analysis": {
        "keywords": ["oil", "prices", "surge", "supply"],
        "sentiment": "negative",
        "topics": ["energy", "markets"],
        "entities": ["oil"]
    },
    "confidence": 0.92,
    "processing_time_ms": 87
}
```

---

## Environment Configuration

### .env.example
```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-change-this
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (for modules)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

# Database (future)
# DATABASE_URL=postgresql://user:pass@localhost/b4

# Redis (future, for Celery)
# REDIS_URL=redis://localhost:6379/0
```

---

## Module Development Pattern

### Creating a New Module

1. **Create module directory**
```bash
mkdir -p modules/interactive/my_module
cd modules/interactive/my_module
touch __init__.py module.py README.md
```

2. **Implement module class**
```python
# module.py
from modules.base import BaseModule, ModuleType

class MyModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.name = "MyModule"
        self.module_type = ModuleType.INTERACTIVE

    async def process(self, input_data):
        # Your logic here
        text = input_data.get("text", "")

        result = {
            "response": f"Processed: {text}",
            "confidence": 0.9
        }

        return result
```

3. **Register in apps.py**
```python
# apps/modules_app/apps.py
from modules.interactive.my_module.module import MyModule
registry.register(MyModule)
```

4. **Test via API**
```bash
curl -X POST http://localhost:8000/api/modules/MyModule/process \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_modules.py
def test_chat_agent_module():
    module = ChatAgentModule()
    result = await module.process({"text": "hello"})
    assert "response" in result
    assert result["confidence"] > 0
```

### Integration Tests
```python
# tests/test_api.py
def test_chat_endpoint(client):
    response = client.post("/api/chat", {
        "text": "hello",
        "user_id": "test"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### Manual Testing with Postman
1. Import collection
2. Set environment variables
3. Run all requests
4. Verify responses

---

## Development Workflow

### 1. Start Django Server
```bash
cd backend
python manage.py runserver
```

### 2. Test with Postman or cURL
```bash
# List modules
curl http://localhost:8000/api/modules

# Send message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "user_id": "test"}'
```

### 3. Add New Module
```bash
# Create module
mkdir -p modules/interactive/new_module
# ... implement module ...

# Restart server (auto-discovery runs)
python manage.py runserver
```

### 4. Verify Module Loaded
```bash
curl http://localhost:8000/api/modules | jq
```

---

## Success Criteria

Phase 1 is complete when:

- ✅ Django server runs without errors
- ✅ Module registry auto-discovers modules
- ✅ REST API responds to all endpoints
- ✅ ChatAgentModule processes messages
- ✅ AnalyzerModule performs analysis
- ✅ Postman collection works end-to-end
- ✅ Can add new module without touching backend code
- ✅ Documentation is clear and complete

---

## Next Phase Preview

**Phase 2: Background Workers & Event Processing**
- Add Celery for background tasks
- Implement event extraction pipeline
- Add Firestore integration
- Create scheduled workers

**Phase 3: Communication Channels**
- Add Telegram webhook
- Add WhatsApp integration
- Add Rocket.Chat connector

---

## Getting Started

```bash
# 1. Clone and setup
cd /Users/ed/King/B4
mkdir backend
cd backend

# 2. Initialize Django
django-admin startproject config .

# 3. Install dependencies
pip install django djangorestframework python-dotenv

# 4. Create apps
python manage.py startapp api apps/api
python manage.py startapp modules_app apps/modules_app
python manage.py startapp core apps/core

# 5. Start building!
```

---

**Document Version**: 1.0
**Last Updated**: November 10, 2025
**Status**: Ready to Implement
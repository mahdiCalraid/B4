# B4 Backend Architecture Plan

**Version**: 1.0
**Date**: November 10, 2025
**Status**: Implementation Ready

---

## Executive Summary

B4's backend is a **Django-based orchestration layer** that acts as the central nervous system connecting:
1. **Communication channels** (Telegram, WhatsApp, Rocket.Chat, REST API)
2. **Processing modules** (AI agents, analyzers, scrapers)
3. **External services** (trading APIs, news sources, databases)

**Key Principle**: The backend is a **thin orchestration layer** that routes requests to appropriate modules and returns responses. It does NOT contain business logic - that lives in modules.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     INTERACTION LAYER                           │
│  (Telegram, WhatsApp, Rocket.Chat, REST API, Postman)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND SERVER                        │
│                  (Routing & Orchestration)                      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Webhook    │  │   REST API   │  │   Task       │         │
│  │   Endpoints  │  │   Endpoints  │  │   Queue      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │           Module Router & Dispatcher             │         │
│  └──────────────────────────────────────────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING MODULES                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Interactive │  │  Background  │  │   External   │         │
│  │   Modules    │  │   Workers    │  │     API      │         │
│  │              │  │              │  │  Connectors  │         │
│  │ • Chat Agent │  │ • News       │  │ • Trading    │         │
│  │ • Analyzer   │  │   Scraper    │  │   APIs       │         │
│  │ • Classifier │  │ • Event      │  │ • Market     │         │
│  │              │  │   Monitor    │  │   Data       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  (Firestore, PostgreSQL, Redis, GCS)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Interaction Layer

### Purpose
Provides multiple interfaces for users and systems to communicate with B4.

### Components

#### 1.1 Messaging Platforms (Webhooks)
- **Telegram**: `/webhook/telegram/`
- **WhatsApp**: `/webhook/whatsapp/`
- **Rocket.Chat**: `/webhook/rocketchat/`

**Flow**:
```
User sends message → Platform posts to webhook → Django receives →
Routes to module → Module processes → Django sends response →
Platform delivers to user
```

#### 1.2 REST API (Direct Access)
- **Development**: Postman, cURL
- **Production**: Web apps, mobile apps, integrations

**Endpoints**:
```
POST /api/chat/message        # Send message for processing
POST /api/analyze/event       # Analyze an event
GET  /api/events/recent       # Get recent events
POST /api/modules/trigger     # Manually trigger a module
```

#### 1.3 Scheduled Tasks
- Cron-like jobs for background workers
- Triggered by Django's Celery or Cloud Scheduler

---

## Layer 2: Django Backend Server

### Purpose
**Thin orchestration layer** that:
1. Receives requests from interaction layer
2. Routes to appropriate module
3. Waits for or schedules processing
4. Returns response to caller

### Key Characteristics
- ✅ **No business logic** (lives in modules)
- ✅ **Simple routing** (which module handles what)
- ✅ **Authentication & authorization**
- ✅ **Request/response transformation**
- ✅ **Error handling & logging**
- ✅ **Rate limiting & quotas**

### Django Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── config/                      # Django project settings
│   ├── __init__.py
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── __init__.py
│   │
│   ├── webhooks/               # Webhook receivers
│   │   ├── __init__.py
│   │   ├── views.py           # Webhook endpoints
│   │   ├── urls.py
│   │   ├── serializers.py     # Request/response models
│   │   └── utils.py           # Webhook validation
│   │
│   ├── api/                    # REST API
│   │   ├── __init__.py
│   │   ├── views.py           # API endpoints
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   └── permissions.py
│   │
│   ├── modules/                # Module management
│   │   ├── __init__.py
│   │   ├── router.py          # Routes requests to modules
│   │   ├── registry.py        # Module registry
│   │   ├── models.py          # Module metadata
│   │   └── tasks.py           # Celery tasks
│   │
│   └── core/                   # Shared utilities
│       ├── __init__.py
│       ├── authentication.py
│       ├── exceptions.py
│       ├── logging.py
│       └── middleware.py
│
└── modules/                    # Actual processing modules
    ├── __init__.py
    ├── base.py                # Base module interface
    │
    ├── interactive/           # User-facing modules
    │   ├── chat_agent/
    │   ├── analyzer/
    │   └── classifier/
    │
    ├── background/            # Autonomous workers
    │   ├── news_scraper/
    │   ├── event_monitor/
    │   └── trend_detector/
    │
    └── connectors/            # External API integrations
        ├── trading_api/
        ├── market_data/
        └── social_media/
```

---

## Layer 3: Processing Modules

### Purpose
Contains **all business logic** for processing requests and performing work.

### Module Types

#### 3.1 Interactive Modules
**Triggered by user messages/requests, return immediate responses**

Examples:
- **ChatAgent**: Conversational AI
- **EventAnalyzer**: Analyzes events and returns insights
- **Classifier**: Classifies content into categories

**Characteristics**:
- Synchronous (user waits for response)
- Response within 1-30 seconds
- Interacts via messaging platforms

#### 3.2 Background Workers
**Run continuously or on schedule, no direct user interaction**

Examples:
- **NewsScraper**: Continuously scrapes news sources
- **EventMonitor**: Watches for specific event patterns
- **TrendDetector**: Analyzes patterns over time

**Characteristics**:
- Asynchronous (run independently)
- Can run for minutes/hours
- Store results in database
- May send notifications when done

#### 3.3 External API Connectors
**Interact with third-party services**

Examples:
- **TradingAPI**: Executes trades on exchanges
- **MarketData**: Fetches real-time market data
- **SocialMedia**: Posts/monitors social platforms

**Characteristics**:
- Can be triggered or autonomous
- Handle authentication with external services
- Manage rate limits and retries

### Base Module Interface

```python
# modules/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class ModuleType(Enum):
    INTERACTIVE = "interactive"
    BACKGROUND = "background"
    CONNECTOR = "connector"

class BaseModule(ABC):
    """Base interface all modules must implement"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.module_type = ModuleType.INTERACTIVE

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method.

        Args:
            input_data: Dictionary containing request data

        Returns:
            Dictionary containing response data
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input before processing"""
        return True

    def get_info(self) -> Dict[str, Any]:
        """Return module metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.module_type.value,
            "description": self.__doc__ or "No description"
        }

    async def health_check(self) -> bool:
        """Check if module is healthy"""
        return True
```

---

## Request Flow Examples

### Example 1: User sends Telegram message

```
1. User: "Analyze the latest oil market news"
   ↓
2. Telegram → POST /webhook/telegram/
   ↓
3. Django WebhookView:
   - Validates webhook signature
   - Extracts message content
   - Identifies user (chat_id)
   ↓
4. Django ModuleRouter:
   - Determines appropriate module: "EventAnalyzer"
   - Calls module.process({"text": "...", "user_id": "..."})
   ↓
5. EventAnalyzer Module:
   - Fetches recent oil events from Firestore
   - Uses AI agent to analyze
   - Returns formatted analysis
   ↓
6. Django WebhookView:
   - Receives module response
   - Sends via Telegram API
   ↓
7. User receives analysis in Telegram
```

### Example 2: Background scraper runs

```
1. Cloud Scheduler: POST /api/modules/trigger
   Body: {"module": "NewsScraper"}
   ↓
2. Django API View:
   - Validates API key
   - Queues task
   ↓
3. Celery Worker:
   - Picks up task
   - Calls NewsScraper.process({})
   ↓
4. NewsScraper Module:
   - Scrapes news sources
   - Extracts events
   - Stores in Firestore
   - Returns summary
   ↓
5. Django logs results
   No user notification (autonomous)
```

### Example 3: Trading API connector

```
1. EventMonitor detects price threshold
   ↓
2. Calls TradingAPI connector internally
   ↓
3. TradingAPI Module:
   - Authenticates with exchange
   - Places trade order
   - Logs transaction
   - Returns confirmation
   ↓
4. EventMonitor logs trade
   Optionally sends Telegram notification
```

---

## Module Registry & Discovery

### Purpose
Centralized registry of all available modules and their capabilities.

### Implementation

```python
# apps/modules/registry.py

from typing import Dict, Type
from modules.base import BaseModule, ModuleType

class ModuleRegistry:
    """Central registry for all processing modules"""

    def __init__(self):
        self._modules: Dict[str, Type[BaseModule]] = {}

    def register(self, module_class: Type[BaseModule]):
        """Register a module"""
        module_name = module_class.__name__
        self._modules[module_name] = module_class
        print(f"✅ Registered module: {module_name}")

    def get_module(self, module_name: str) -> BaseModule:
        """Get module instance by name"""
        if module_name not in self._modules:
            raise ValueError(f"Module '{module_name}' not found")
        return self._modules[module_name]()

    def list_modules(self, module_type: ModuleType = None) -> Dict[str, Dict]:
        """List all registered modules"""
        modules = {}
        for name, module_class in self._modules.items():
            instance = module_class()
            if module_type is None or instance.module_type == module_type:
                modules[name] = instance.get_info()
        return modules

# Global registry instance
registry = ModuleRegistry()
```

### Module Registration (Auto-discovery)

```python
# apps/modules/apps.py

from django.apps import AppConfig

class ModulesConfig(AppConfig):
    name = 'apps.modules'

    def ready(self):
        """Auto-discover and register all modules on startup"""
        from .registry import registry

        # Import and register interactive modules
        from modules.interactive.chat_agent.module import ChatAgentModule
        from modules.interactive.analyzer.module import AnalyzerModule

        registry.register(ChatAgentModule)
        registry.register(AnalyzerModule)

        # Import and register background workers
        from modules.background.news_scraper.module import NewsScraperModule

        registry.register(NewsScraperModule)

        # ... etc

        print(f"\n📦 Registered {len(registry._modules)} modules\n")
```

---

## Request Routing Logic

### Simple Pattern-Based Routing

```python
# apps/modules/router.py

from typing import Dict, Any
from .registry import registry

class ModuleRouter:
    """Routes requests to appropriate modules"""

    def __init__(self):
        self.registry = registry

    async def route(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to appropriate module based on content.

        Args:
            request_data: {
                "text": "user message",
                "user_id": "123",
                "source": "telegram",
                "module": "ChatAgent"  # Optional: explicit module
            }

        Returns:
            Module processing result
        """
        # Explicit module specified
        if "module" in request_data:
            module_name = request_data["module"]
            module = self.registry.get_module(module_name)
            return await module.process(request_data)

        # Infer module from content
        module_name = self._infer_module(request_data)
        module = self.registry.get_module(module_name)

        return await module.process(request_data)

    def _infer_module(self, request_data: Dict[str, Any]) -> str:
        """
        Infer which module should handle this request.

        Simple rules for now, can be replaced with classifier later.
        """
        text = request_data.get("text", "").lower()

        # Keyword-based routing
        if any(word in text for word in ["analyze", "analysis", "what happened"]):
            return "AnalyzerModule"

        if any(word in text for word in ["classify", "category", "type"]):
            return "ClassifierModule"

        # Default to chat agent
        return "ChatAgentModule"

# Global router instance
router = ModuleRouter()
```

---

## Django Apps Implementation

### Webhooks App

```python
# apps/webhooks/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from apps.modules.router import router

@csrf_exempt
@require_POST
async def telegram_webhook(request):
    """
    Telegram webhook endpoint.

    Receives messages from Telegram and routes to modules.
    """
    try:
        # Parse payload
        payload = json.loads(request.body)

        # Extract message
        message = payload.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")

        # Route to module
        result = await router.route({
            "text": text,
            "user_id": str(user_id),
            "chat_id": str(chat_id),
            "source": "telegram",
            "raw_payload": payload
        })

        # Send response back via Telegram
        from connectors.telegram import send_message
        await send_message(chat_id, result.get("response", "Processed"))

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

### API App

```python
# apps/api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.modules.router import router
from apps.modules.registry import registry

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def chat_message(request):
    """
    Send a message for processing.

    POST /api/chat/message
    {
        "text": "Analyze oil markets",
        "module": "AnalyzerModule"  # optional
    }
    """
    result = await router.route(request.data)
    return Response(result)

@api_view(['GET'])
async def list_modules(request):
    """
    List all available modules.

    GET /api/modules/list
    """
    module_type = request.query_params.get("type")
    modules = registry.list_modules(module_type)
    return Response(modules)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def trigger_module(request):
    """
    Manually trigger a specific module.

    POST /api/modules/trigger
    {
        "module": "NewsScraperModule",
        "params": {}
    }
    """
    module_name = request.data.get("module")
    params = request.data.get("params", {})

    module = registry.get_module(module_name)
    result = await module.process(params)

    return Response(result)
```

---

## Background Tasks (Celery)

### Setup

```python
# config/celery.py

from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('b4_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Task Definition

```python
# apps/modules/tasks.py

from celery import shared_task
from .registry import registry

@shared_task
def run_background_module(module_name: str, params: dict):
    """
    Run a background module asynchronously.

    Usage:
        run_background_module.delay("NewsScraperModule", {})
    """
    module = registry.get_module(module_name)
    result = module.process(params)
    return result

@shared_task
def scheduled_scraper():
    """Run news scraper on schedule"""
    return run_background_module("NewsScraperModule", {})
```

---

## Configuration Management

### Environment Variables

```bash
# .env

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@localhost/b4

# Firestore
GOOGLE_CLOUD_PROJECT=your-project-id

# External APIs
TELEGRAM_BOT_TOKEN=your-token
WHATSAPP_TOKEN=your-token

# AI Services
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Settings Structure

```python
# config/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # B4 Apps
    'apps.webhooks',
    'apps.api',
    'apps.modules',
    'apps.core',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'b4'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
```

---

## Deployment Considerations

### Development
- SQLite for quick setup
- Django dev server
- No Celery (synchronous processing)

### Production
- PostgreSQL database
- Gunicorn/Uvicorn ASGI server
- Celery + Redis for background tasks
- Cloud Run or Kubernetes

---

## Summary of Responsibilities

### Django Backend
- ✅ Receive requests from interaction layer
- ✅ Validate and authenticate requests
- ✅ Route to appropriate module
- ✅ Transform responses for each platform
- ✅ Handle errors gracefully
- ✅ Log all interactions
- ❌ **NO business logic**

### Processing Modules
- ✅ All business logic
- ✅ AI agent execution
- ✅ Data processing and analysis
- ✅ External API interactions
- ✅ Database operations
- ❌ **NO routing logic**

---

## Next Steps

1. ✅ **Review and approve this architecture**
2. Set up Django project structure
3. Implement base module interface
4. Create module registry and router
5. Build first interactive module (ChatAgent)
6. Add Telegram webhook
7. Test end-to-end flow
8. Add more modules incrementally

---

**Document Version**: 1.0
**Last Updated**: November 10, 2025
**Status**: Ready for Review
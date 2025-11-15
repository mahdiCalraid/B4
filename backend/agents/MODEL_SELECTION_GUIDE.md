# AI Model Selection Guide

## Overview

The B4 Agent System now supports dynamic model selection, allowing you to use different AI models with any agent without changing code. Simply specify the `model` parameter in your API request or function call.

## Supported Models

### Gemini Models (Google AI)
- **gemini-2.0-flash-exp** - Latest experimental (1M context, fast)
- **gemini-2.0-flash** - Stable version (1M context)
- **gemini-1.5-pro** - Highest quality (2M context)
- **gemini-1.5-flash** - Balanced (1M context)

### OpenAI Models (GPT)
- **gpt-4o** - GPT-4 Omni flagship (128K context)
- **gpt-4o-mini** - Affordable and fast (128K context)
- **gpt-4-turbo** - High performance (128K context)
- **gpt-4-turbo-2024-04-09** - April 2024 snapshot
- **gpt-3.5-turbo** - Cost-effective (16K context)

### Groq Models (Ultra-fast inference)
- **llama-3.3-70b-versatile** - LLaMA 3.3 70B (8K context)
- **llama-3.3-70b-specdec** - With speculative decoding
- **llama-3.1-70b-versatile** - LLaMA 3.1 70B (131K context)
- **llama-3.1-8b-instant** - Instant responses (131K context)
- **mixtral-8x7b-32768** - Mixtral MoE (32K context)

### Ollama Models (Local/Private)
- **llama3.2** - LLaMA 3.2 local (128K context)
- **llama3.1** - LLaMA 3.1 local (128K context)
- **gemma2** - Google's Gemma 2 (8K context)

## Model Aliases

For convenience, several aliases are supported:

- **gpt-oss-20b** → `gpt-4o-mini`
- **gpt4** → `gpt-4o`
- **gpt4o** → `gpt-4o`
- **gpt4-mini** → `gpt-4o-mini`
- **gemini** → `gemini-2.0-flash-exp`
- **gemini-flash** → `gemini-2.0-flash`
- **gemini-pro** → `gemini-1.5-pro`
- **llama** → `llama-3.3-70b-versatile`
- **llama3.3** → `llama-3.3-70b-versatile`
- **mixtral** → `mixtral-8x7b-32768`

## Usage

### HTTP API

#### Basic Request (Default Model)
```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{"input": "John went to Paris"}'
```

#### Specify Model
```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John went to Paris",
    "model": "gpt-4o"
  }'
```

#### Use Model Alias
```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John went to Paris",
    "model": "gpt-oss-20b"
  }'
```

### Python Function Call

```python
from agents.agent_loader import AgentLoader

loader = AgentLoader()
agent = loader.load_agent("agent_mother")

# Use default model
result = await agent.process("John went to Paris")

# Use specific model
result = await agent.process("John went to Paris", model="gpt-4o")

# Use model alias
result = await agent.process("John went to Paris", model="gpt-oss-20b")
```

### Direct Model Selector

```python
from agents.general_codes.ai_model_selector import get_model_selector

selector = get_model_selector()

# Generate text
text = await selector.generate(
    input_text="Tell me about Paris",
    model="gpt-4o",
    system_prompt="You are a helpful assistant"
)

# Generate structured output
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    country: str
    population: int

result = await selector.generate_structured(
    input_text="Tell me about Paris",
    output_schema=CityInfo,
    model="gemini-2.0-flash"
)
```

## API Endpoints

### List All Models
```bash
GET /agents/models/list
```

Response:
```json
{
  "success": true,
  "count": 17,
  "models": {
    "gemini-2.0-flash-exp": {
      "provider": "gemini",
      "name": "gemini-2.0-flash-exp",
      "supports_structured": true,
      "context_window": 1000000,
      "description": "Latest Gemini 2.0 Flash experimental"
    },
    ...
  }
}
```

### List Models by Provider
```bash
GET /agents/models/list?provider=gemini
GET /agents/models/list?provider=openai
GET /agents/models/list?provider=groq
GET /agents/models/list?provider=ollama
```

### Get Model Info
```bash
GET /agents/models/{model_name}
```

Example:
```bash
curl http://localhost:8080/agents/models/gpt-oss-20b
```

Response:
```json
{
  "success": true,
  "model": {
    "provider": "openai",
    "name": "gpt-4o-mini",
    "resolved_name": "gpt-4o-mini",
    "supports_structured": true,
    "context_window": 128000,
    "description": "GPT-4 Omni Mini - affordable and fast"
  }
}
```

## Structured Output Support

All models support structured output through different mechanisms:

### Gemini
- Uses native JSON mode (`response_mime_type="application/json"`)
- Highly reliable structured output

### OpenAI
- Uses function calling for structured output
- Extremely reliable with schema validation

### Groq
- Uses JSON mode (`response_format={"type": "json_object"}`)
- Fast and reliable

### Ollama
- Uses prompt-based JSON generation
- Works well for simple schemas

## Best Practices

### 1. Choose Model by Task

**For Entity Extraction:**
- Fast: `gemini-2.0-flash`, `llama-3.1-8b-instant`
- Accurate: `gpt-4o`, `gemini-1.5-pro`

**For Analysis:**
- Fast: `gpt-4o-mini`, `gemini-2.0-flash`
- Deep: `gpt-4o`, `gemini-1.5-pro`

**For Large Context:**
- `gemini-1.5-pro` (2M tokens)
- `llama-3.1-70b-versatile` (131K tokens)
- `gpt-4o` (128K tokens)

**For Privacy:**
- `llama3.2` (local)
- `llama3.1` (local)
- `gemma2` (local)

### 2. Model Selection Strategy

```python
# Fast prototyping
model = "gemini-2.0-flash"

# Production quality
model = "gpt-4o"

# Cost-effective
model = "gpt-4o-mini"

# Maximum context
model = "gemini-1.5-pro"

# Ultra-fast inference
model = "llama-3.3-70b-versatile"  # via Groq

# Privacy-first
model = "llama3.2"  # local via Ollama
```

### 3. Fallback Strategy

```python
# Try fast model first, fallback to powerful model
try:
    result = await agent.process(input, model="gemini-2.0-flash")
except:
    result = await agent.process(input, model="gpt-4o")
```

## Environment Variables

Required API keys (set in [run.sh](file:///Users/ed/King/B4/backend/run.sh) or environment):

```bash
export GEMINI_API_KEY="your_gemini_key"      # For Gemini models
export OPENAI_API_KEY="your_openai_key"      # For OpenAI models
export GROQ_API_KEY="your_groq_key"          # For Groq models
# Ollama requires local installation (no API key)
```

## Examples

### Compare Models

```python
test_input = "Apple announced iPhone 15 in Cupertino on September 12."

models_to_test = [
    "gemini-2.0-flash",
    "gpt-4o",
    "llama-3.3-70b-versatile"
]

for model in models_to_test:
    result = await agent.process(test_input, model=model)
    print(f"{model}: {result}")
```

### Production Pattern

```python
class AIService:
    def __init__(self):
        self.loader = AgentLoader()

    async def extract_entities(
        self,
        text: str,
        quality: str = "balanced"
    ):
        agent = self.loader.load_agent("agent_mother")

        # Select model based on quality tier
        models = {
            "fast": "gemini-2.0-flash",
            "balanced": "gpt-4o-mini",
            "high": "gpt-4o",
            "local": "llama3.2"
        }

        model = models.get(quality, "gemini-2.0-flash")

        return await agent.process(text, model=model)
```

## Troubleshooting

### Model Not Found
If you get "Model not found", check available models:
```bash
curl http://localhost:8080/agents/models/list
```

### API Key Error
Ensure the required API key is set:
```bash
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
```

### Structured Output Fails
Some models handle structured output better than others. If you get parsing errors, try:
1. Gemini models (best structured output support)
2. OpenAI models (excellent function calling)
3. Simpler schema

## Testing

Run comprehensive model tests:
```bash
cd /Users/ed/King/B4/backend
./test_model_selection.sh
```

This tests:
- Model listing
- Model aliases
- Different agents with different models
- Structured output across providers

## Adding New Models

To add a new model, edit [ai_model_selector.py](file:///Users/ed/King/B4/backend/agents/general_codes/ai_model_selector.py):

```python
MODEL_REGISTRY = {
    "your-new-model": {
        "provider": "provider_name",
        "name": "your-new-model",
        "supports_structured": True,
        "context_window": 128000,
        "description": "Description"
    }
}
```

## Summary

- **17+ models** across 4 providers
- **Structured output** on all models
- **Model aliases** for convenience
- **Dynamic selection** via API or code
- **No code changes** required to switch models
- **Provider fallbacks** supported

Use the `model` parameter to leverage the best AI model for each task!

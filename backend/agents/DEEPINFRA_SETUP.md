# DeepInfra Setup Guide for gpt-oss-20b

## Overview

The `gpt-oss-20b` model is now properly configured to use **DeepInfra** (not OpenAI). DeepInfra provides access to the open-source GPT-OSS 20B model, which is a 21 billion parameter Mixture-of-Experts (MoE) model released by OpenAI under the Apache 2.0 license.

## Model Details

- **Model Name**: `openai/gpt-oss-20b`
- **Provider**: DeepInfra
- **Parameters**: 21B total (3.6B active per forward pass)
- **Architecture**: Mixture-of-Experts (MoE)
- **Context Window**: 8,192 tokens
- **License**: Apache 2.0 (open-source)
- **Features**: Structured output, JSON mode, function calling

## Quick Start

### 1. Get DeepInfra API Key

Sign up for DeepInfra at [https://deepinfra.com](https://deepinfra.com) and get your API key.

### 2. Set Environment Variable

Add your API key to [run.sh](file:///Users/ed/King/B4/backend/run.sh):

```bash
export DEEPINFRA_API_KEY="your_actual_api_key_here"
```

Or set it in your shell:

```bash
export DEEPINFRA_API_KEY="di_xxxxxxxxxxxxx"
```

### 3. Test the Model

```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John Smith went to Paris",
    "model": "gpt-oss-20b"
  }'
```

## API Endpoint Details

### DeepInfra Endpoint
- **Base URL**: `https://api.deepinfra.com/v1/openai`
- **Endpoint**: `/chat/completions`
- **Authentication**: Bearer token in Authorization header
- **Compatibility**: OpenAI-compatible API

### Model Name in API
When using the DeepInfra API directly, use:
```
model: "openai/gpt-oss-20b"
```

In B4 agents, you can use either:
- `"gpt-oss-20b"` (short name)
- `"openai/gpt-oss-20b"` (full name)

## Features Supported

### ✅ Structured Output
The model supports structured JSON output via `response_format: {"type": "json_object"}`.

Example:
```python
from agents.agent_loader import AgentLoader

loader = AgentLoader()
agent = loader.load_agent("agent_mother")

result = await agent.process(
    "Elon Musk visited SpaceX in California",
    model="gpt-oss-20b"
)

# Returns structured JSON with people and places
```

### ✅ JSON Mode
All responses can be forced to valid JSON format.

### ✅ Fast Inference
DeepInfra optimizes inference for low latency.

### ✅ Cost-Effective
Pay-as-you-go pricing, typically cheaper than proprietary models.

## Configuration Check

### Verify Model is Registered
```bash
curl http://localhost:8080/agents/models/gpt-oss-20b
```

Expected response:
```json
{
  "success": true,
  "model": {
    "provider": "deepinfra",
    "name": "openai/gpt-oss-20b",
    "supports_structured": true,
    "supports_json_mode": true,
    "context_window": 8192,
    "description": "GPT-OSS 20B - Open-source 21B param MoE model via DeepInfra"
  }
}
```

### Verify Provider is Configured
```bash
curl http://localhost:8080/agents/models/list?provider=deepinfra
```

## Implementation Details

### DeepInfra Agent ([deepinfra_agent.py](file:///Users/ed/King/B4/backend/modules/agents/deepinfra_agent.py))

The DeepInfra agent uses the OpenAI-compatible interface:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://api.deepinfra.com/v1/openai",
    api_key=os.getenv("DEEPINFRA_API_KEY")
)
```

This allows seamless integration with structured output and JSON mode.

### Model Registry Entry

In [ai_model_selector.py](file:///Users/ed/King/B4/backend/agents/general_codes/ai_model_selector.py):

```python
"gpt-oss-20b": {
    "provider": "deepinfra",
    "name": "openai/gpt-oss-20b",
    "supports_structured": True,
    "supports_json_mode": True,
    "context_window": 8192,
    "description": "GPT-OSS 20B - Open-source MoE model via DeepInfra"
}
```

## Usage Examples

### With Agent Mother
```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Marie Curie worked in Paris at the Radium Institute",
    "model": "gpt-oss-20b"
  }'
```

Response:
```json
{
  "success": true,
  "agent_id": "agent_mother",
  "data": {
    "people": [
      {"first_name": "Marie", "last_name": "Curie", "full_name": "Marie Curie"}
    ],
    "places": [
      {"name": "Paris", "type": "city"},
      {"name": "Radium Institute", "type": "building"}
    ]
  },
  "model": "gpt-oss-20b"
}
```

### With Test Agent
```bash
curl -X POST http://localhost:8080/agents/test_agent \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Tesla announced Cybertruck production in Austin, Texas",
    "model": "gpt-oss-20b"
  }'
```

### Python Code
```python
from agents.general_codes.ai_model_selector import get_model_selector

selector = get_model_selector()

# Text generation
text = await selector.generate(
    input_text="Tell me about Paris",
    model="gpt-oss-20b",
    system_prompt="You are a helpful assistant"
)

# Structured output
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    country: str
    famous_for: list[str]

result = await selector.generate_structured(
    input_text="Tell me about Paris",
    output_schema=CityInfo,
    model="gpt-oss-20b"
)
```

## Troubleshooting

### Error: "DEEPINFRA_API_KEY not found"
**Solution**: Set the environment variable:
```bash
export DEEPINFRA_API_KEY="your_key"
```

### Error: "AsyncClient.__init__() got unexpected keyword argument 'proxies'"
**Solution**: This was the old error when gpt-oss-20b was incorrectly mapped to OpenAI. It's now fixed to use DeepInfra.

### Model returns invalid JSON
**Solution**: Ensure your prompt includes instructions to return JSON:
```python
system_prompt = "You must respond with valid JSON matching the schema."
```

### Slow responses
**Solution**: DeepInfra should be fast. Check:
- Network connectivity
- Model availability (sometimes models are cold-starting)
- Try a different region if available

## Comparison with Other Models

| Feature | gpt-oss-20b (DeepInfra) | gpt-4o-mini (OpenAI) | gemini-2.0-flash (Google) |
|---------|-------------------------|----------------------|---------------------------|
| Provider | DeepInfra | OpenAI | Google |
| Cost | Low | Medium | Low |
| Speed | Fast | Medium | Very Fast |
| Context | 8K | 128K | 1M |
| Open Source | ✅ Yes | ❌ No | ❌ No |
| Structured Output | ✅ | ✅ | ✅ |
| Privacy | Self-hostable | Cloud only | Cloud only |

## Best Use Cases

### ✅ Good For:
- Entity extraction
- Text classification
- Structured data extraction
- Cost-sensitive applications
- Open-source requirement
- Moderate context needs

### ⚠️ Less Ideal For:
- Very long context (>8K tokens)
- Complex reasoning requiring larger models
- Tasks requiring latest GPT-4 level capabilities

## Additional Resources

- **DeepInfra Docs**: [https://deepinfra.com/docs](https://deepinfra.com/docs)
- **DeepInfra API Reference**: [https://deepinfra.com/openai/gpt-oss-20b/api](https://deepinfra.com/openai/gpt-oss-20b/api)
- **GPT-OSS Announcement**: [https://openai.com/index/introducing-gpt-oss/](https://openai.com/index/introducing-gpt-oss/)
- **Model on Hugging Face**: [https://huggingface.co/openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)

## Summary

✅ **gpt-oss-20b now correctly uses DeepInfra**
- Previously incorrectly aliased to OpenAI gpt-4o-mini
- Now properly configured with DeepInfraAgent
- Requires DEEPINFRA_API_KEY environment variable
- Full structured output support
- OpenAI-compatible API interface
- Fast, cost-effective, and open-source

Set your API key and start using it! 🚀

# B4 Agent System

A flexible, file-based agent system that integrates seamlessly with the B4 backend infrastructure.

## Overview

The B4 Agent System allows you to create AI agents using simple file-based definitions. Each agent is a folder containing configuration files that define its behavior, without requiring code changes to the backend.

## Architecture

```
agents/
├── __init__.py
├── base_agent.py              # Base agent class
├── agent_loader.py            # Agent discovery and loading
├── general_codes/             # Shared utilities
│   ├── ai_api_call.py        # AI API calling
│   ├── prompt_reader.py      # Prompt handling
│   ├── structure_handler.py  # Output structure validation
│   ├── result_handler.py     # Result processing
│   └── tools_caller.py       # Tool calling utilities
└── agent_definitions/         # Agent instances
    └── agent_mother/         # Example agent
        ├── info.txt          # Agent metadata
        ├── prompt.txt        # System prompt
        └── structure_output.json  # Output schema
```

## Creating a New Agent

### 1. Create Agent Folder

Create a new folder in `agents/agent_definitions/`:

```bash
mkdir agents/agent_definitions/agent_my_agent
```

### 2. Create info.txt

Define agent metadata:

```
name: My Agent
description: A brief description of what this agent does
role: Specific role and task of the agent
input: Description of expected input
output: Description of expected output
version: 1.0
author: Your Name
created: 2024-11-14
```

### 3. Create prompt.txt

Define the system prompt:

```
You are an expert at [specific task].

Your task is to [detailed instructions].

Guidelines:
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

Return your response as a structured JSON object matching the required schema.
```

### 4. Create structure_output.json

Define the output schema (JSON Schema format):

```json
{
  "type": "object",
  "properties": {
    "field1": {
      "type": "string",
      "description": "Description of field1"
    },
    "field2": {
      "type": "array",
      "description": "Description of field2",
      "items": {
        "type": "object",
        "properties": {
          "subfield": {
            "type": "string"
          }
        }
      }
    }
  },
  "required": ["field1", "field2"]
}
```

### 5. Optional Files

- `config.py`: Python configuration (advanced settings)
- `special_tools.py`: Agent-specific tools and functions

## Using Agents

### Method 1: Direct Function Call

```python
from agents.agent_loader import AgentLoader

# Create loader
loader = AgentLoader()

# Load agent
agent = loader.load_agent("agent_mother")

# Process input
result = await agent.process("Your input text here")

print(result)
```

### Method 2: HTTP API

#### List All Agents

```bash
curl http://localhost:8080/agents/
```

#### Get Agent Info

```bash
curl http://localhost:8080/agents/agent_mother
```

#### Process with Agent

```bash
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{"input": "Your input text here"}'
```

#### Get Detailed Info

```bash
curl http://localhost:8080/agents/agent_mother/info
```

## Example: agent_mother

The `agent_mother` is a template agent that extracts people and places from text.

### Input

```json
{
  "input": "John Smith and Jane Doe traveled to Paris, France last week."
}
```

### Output

```json
{
  "success": true,
  "agent_id": "agent_mother",
  "data": {
    "people": [
      {
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith"
      },
      {
        "first_name": "Jane",
        "last_name": "Doe",
        "full_name": "Jane Doe"
      }
    ],
    "places": [
      {
        "name": "Paris",
        "type": "city"
      },
      {
        "name": "France",
        "type": "country"
      }
    ]
  },
  "provider": "gemini"
}
```

## AI Providers

The system supports multiple AI providers:

- **Gemini** (default): Fast, cost-effective
- **OpenAI**: GPT-4 and GPT-3.5 models
- **Groq**: Ultra-fast inference
- **Ollama**: Local models

### Specify Provider

#### Python

```python
agent = loader.load_agent("agent_mother", provider="openai")
```

#### HTTP API

```json
{
  "input": "Your text",
  "provider": "openai"
}
```

## Testing

### Test Script (Python)

```bash
cd backend
./venv/bin/python test_agent_mother.py
```

### Test Script (HTTP)

```bash
cd backend
./test_agent_endpoints.sh
```

## Advanced Features

### Custom Tools

Create `special_tools.py` in your agent folder:

```python
from agents.general_codes.tools_caller import register_tool

@register_tool("my_custom_tool", "Description of tool")
def my_tool(param: str) -> str:
    # Implementation
    return result
```

### Custom Configuration

Create `config.py` in your agent folder:

```python
# Agent-specific configuration
TEMPERATURE = 0.5
MAX_TOKENS = 2000
CUSTOM_SETTING = "value"
```

## Best Practices

1. **Clear Prompts**: Be specific about what the agent should do
2. **Structured Output**: Always define a JSON schema for consistent results
3. **Error Handling**: Consider edge cases in your prompt
4. **Testing**: Test with various inputs before deploying
5. **Documentation**: Keep info.txt updated with accurate descriptions

## Troubleshooting

### Agent Not Found

- Check that the agent folder exists in `agents/agent_definitions/`
- Ensure `prompt.txt` exists (minimum requirement)

### API Key Errors

- Set `GEMINI_API_KEY` environment variable
- Or add to `backend/run.sh`

### Invalid Output

- Verify `structure_output.json` is valid JSON Schema
- Check that prompt instructs the AI to follow the schema
- Try with a different provider (e.g., Gemini vs OpenAI)

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agents/` | List all agents |
| GET | `/agents/{agent_id}` | Get agent metadata |
| GET | `/agents/{agent_id}/info` | Get detailed agent info |
| POST | `/agents/{agent_id}` | Process input with agent |

### Request Schema

```json
{
  "input": "string (required)",
  "provider": "string (optional): gemini|openai|groq|ollama"
}
```

### Response Schema

```json
{
  "success": true,
  "agent_id": "string",
  "data": {
    // Agent-specific structured output
  },
  "provider": "string"
}
```

## Contributing

To add a new agent:

1. Create folder in `agent_definitions/`
2. Add required files (info.txt, prompt.txt, structure_output.json)
3. Test with both function calls and HTTP API
4. Document the agent's purpose and usage

## License

Part of the B4 project.

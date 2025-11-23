# Attention Filter Agent

## Purpose
The `attention_filter` agent is the first stage in the B4 memory waterfall pipeline. It performs fast triage to determine if an input is worth processing through the full memory formation pipeline.

## How It Works
1. Analyzes input for relevance (0-1 score)
2. Assesses importance (0-1 score)
3. Detects domains (tech, business, personal, etc.)
4. Identifies entities (people, organizations, places)
5. Recognizes information signals (announcement, meeting, prediction, etc.)
6. Makes a decision: process or skip

## Decision Logic
- **Process if**: relevance_score > 0.3 AND importance_score > 0.2
- **Skip if**: spam, too short (<10 words), or below thresholds

## Usage

### Via API Endpoint
```bash
curl -X POST http://localhost:8080/agents/attention_filter \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Elon Musk announced SpaceX will go to Mars in 2030",
    "model": "gpt-oss-20b"
  }'
```

### Response Structure
```json
{
  "success": true,
  "agent_id": "attention_filter",
  "data": {
    "should_process": true,
    "relevance_score": 0.9,
    "importance_score": 0.8,
    "detected_domains": ["tech", "science"],
    "entity_hints": [
      {"text": "Elon Musk", "type": "person"},
      {"text": "SpaceX", "type": "organization"},
      {"text": "Mars", "type": "place"}
    ],
    "information_signals": ["announcement", "prediction"],
    "skip_reason": null,
    "reasoning": "High relevance tech/space content with known entities and future prediction"
  }
}
```

## Files
- `info.txt` - Agent metadata
- `prompt.txt` - System prompt for the AI
- `structure_output.json` - Output schema definition

## Model Support
Works with any model that supports structured output:
- `gpt-oss-20b` (recommended - fast and cheap)
- `gemini-2.0-flash-lite` (very fast)
- `gemini-2.0-flash` (better quality)
- `gpt-4o-mini` (high quality)
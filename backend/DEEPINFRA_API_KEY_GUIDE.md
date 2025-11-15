# How to Get DeepInfra API Key

## Quick Start (5 minutes)

### Step 1: Sign Up
1. Go to [https://deepinfra.com](https://deepinfra.com)
2. Click "Sign Up" or "Get Started"
3. Create account with email or GitHub

### Step 2: Get API Key
1. Once logged in, go to [https://deepinfra.com/dash/api_keys](https://deepinfra.com/dash/api_keys)
2. Click "Create API Key"
3. Give it a name (e.g., "B4 Development")
4. Copy the key (starts with `di_`)

### Step 3: Set Environment Variable

**In your terminal:**
```bash
export DEEPINFRA_API_KEY="di_your_actual_key_here"
```

**Or in [run.sh](file:///Users/ed/King/B4/backend/run.sh):**
```bash
export DEEPINFRA_API_KEY="di_your_actual_key_here"
```

### Step 4: Test It

**Option 1: Direct curl test**
```bash
curl "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \
  -d '{
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Option 2: B4 test script**
```bash
cd /Users/ed/King/B4/backend
export DEEPINFRA_API_KEY="your_key"
./venv/bin/python test_deepinfra.py
```

**Option 3: Via API endpoint**
```bash
# Make sure server is running with API key set
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John Smith went to Paris",
    "model": "gpt-oss-20b"
  }'
```

## Pricing

DeepInfra offers:
- **Free tier**: Limited credits for testing
- **Pay-as-you-go**: $0.07 per 1M tokens for gpt-oss-20b
- **Much cheaper than OpenAI GPT-4**

Check current pricing: [https://deepinfra.com/pricing](https://deepinfra.com/pricing)

## Troubleshooting

### "401 Unauthorized"
- Your API key is invalid or expired
- Make sure you copied the full key (starts with `di_`)
- Try creating a new key

### "DEEPINFRA_API_KEY not found in environment"
- The environment variable is not set
- Run: `echo $DEEPINFRA_API_KEY` to verify
- If empty, export it again

### "Model not found: openai/gpt-oss-20b"
- Check the model name is correct
- Try listing available models at DeepInfra
- Some models may be in beta or unavailable

### Still not working?
Run the test script with debugging:
```bash
export DEEPINFRA_API_KEY="your_key"
./venv/bin/python test_deepinfra.py
```

This will show exactly where the issue is.

## API Key Security

**DO NOT**:
- ❌ Commit API keys to Git
- ❌ Share API keys publicly
- ❌ Use production keys in development

**DO**:
- ✅ Use environment variables
- ✅ Rotate keys periodically
- ✅ Set spending limits
- ✅ Use separate keys for dev/prod

## Alternative: Test Without DeepInfra

If you don't want to use DeepInfra, you can test with other models:

```bash
# Use Gemini (free, requires GEMINI_API_KEY)
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John Smith went to Paris",
    "model": "gemini-2.0-flash"
  }'

# Use OpenAI (requires OPENAI_API_KEY)
curl -X POST http://localhost:8080/agents/agent_mother \
  -H "Content-Type: application/json" \
  -d '{
    "input": "John Smith went to Paris",
    "model": "gpt-4o-mini"
  }'
```

## Summary

1. Go to https://deepinfra.com/dash/api_keys
2. Create API key (starts with `di_`)
3. Export it: `export DEEPINFRA_API_KEY="di_..."`
4. Test with: `./venv/bin/python test_deepinfra.py`

That's it! 🚀

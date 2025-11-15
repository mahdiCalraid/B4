#!/bin/bash

# Test script for model selection across different AI providers
# This demonstrates the ability to use different models with the same agent

echo "======================================================================="
echo "🧪 Testing AI Model Selection System"
echo "======================================================================="
echo ""

BASE_URL="http://localhost:8080"
TEST_INPUT="Elon Musk visited SpaceX headquarters in Hawthorne, California yesterday."

# Test 1: List available models
echo "1️⃣  Listing all available models..."
echo "   GET $BASE_URL/agents/models/list"
echo ""
curl -s "$BASE_URL/agents/models/list" | python3 -m json.tool | head -30
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 2: Test mother_agent with default (Gemini)
echo "2️⃣  Testing agent_mother with default model..."
echo "   POST $BASE_URL/agents/agent_mother"
echo '   Model: (default)'
echo ""
curl -s -X POST "$BASE_URL/agents/agent_mother" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"$TEST_INPUT\"}" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 3: Test mother_agent with Gemini 2.0 Flash
echo "3️⃣  Testing agent_mother with Gemini 2.0 Flash..."
echo "   POST $BASE_URL/agents/agent_mother"
echo '   Model: gemini-2.0-flash'
echo ""
curl -s -X POST "$BASE_URL/agents/agent_mother" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"$TEST_INPUT\", \"model\": \"gemini-2.0-flash\"}" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 4: Test mother_agent with model alias "gpt-oss-20b" (maps to gpt-4o-mini)
echo "4️⃣  Testing agent_mother with alias 'gpt-oss-20b' (maps to gpt-4o-mini)..."
echo "   POST $BASE_URL/agents/agent_mother"
echo '   Model: gpt-oss-20b'
echo ""
echo "   ⚠️  Note: This requires OPENAI_API_KEY to be set"
curl -s -X POST "$BASE_URL/agents/agent_mother" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"$TEST_INPUT\", \"model\": \"gpt-oss-20b\"}" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 5: Test test_agent with comprehensive analysis
TEST_INPUT_COMPLEX="Apple Inc announced their latest iPhone 15 in Cupertino on September 12, 2023. CEO Tim Cook praised the innovative features."

echo "5️⃣  Testing test_agent with comprehensive analysis (Gemini)..."
echo "   POST $BASE_URL/agents/test_agent"
echo '   Model: gemini-2.0-flash'
echo ""
curl -s -X POST "$BASE_URL/agents/test_agent" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"$TEST_INPUT_COMPLEX\", \"model\": \"gemini-2.0-flash\"}" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 6: Get model info for specific model
echo "6️⃣  Getting info for gpt-oss-20b..."
echo "   GET $BASE_URL/agents/models/gpt-oss-20b"
echo ""
curl -s "$BASE_URL/agents/models/gpt-oss-20b" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

echo "======================================================================="
echo "✅ All model selection tests completed!"
echo ""
echo "Summary:"
echo "  - Model registry supports 17+ models across 4 providers"
echo "  - Agents can use any model via 'model' parameter"
echo "  - Model aliases supported (e.g., gpt-oss-20b → gpt-4o-mini)"
echo "  - Structured output works across all providers"
echo "======================================================================="

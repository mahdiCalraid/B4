#!/bin/bash

# Test script for agent endpoints
# This demonstrates all the ways to interact with the agent system

echo "======================================================================="
echo "🧪 Testing Agent System Endpoints"
echo "======================================================================="
echo ""

BASE_URL="http://localhost:8080"

# Test 1: List all agents
echo "1️⃣  Listing all agents..."
echo "   GET $BASE_URL/agents/"
echo ""
curl -s "$BASE_URL/agents/" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 2: Get agent info (metadata)
echo "2️⃣  Getting agent_mother metadata..."
echo "   GET $BASE_URL/agents/agent_mother"
echo ""
curl -s "$BASE_URL/agents/agent_mother" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 3: Get detailed agent info
echo "3️⃣  Getting detailed agent_mother info..."
echo "   GET $BASE_URL/agents/agent_mother/info"
echo ""
curl -s "$BASE_URL/agents/agent_mother/info" | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 4: Process with agent (simple example)
echo "4️⃣  Processing text with agent_mother (Simple)..."
echo '   POST $BASE_URL/agents/agent_mother'
echo '   Body: {"input": "Alice went to Tokyo."}'
echo ""
curl -s -X POST "$BASE_URL/agents/agent_mother" \
  -H "Content-Type: application/json" \
  -d '{"input": "Alice went to Tokyo."}' | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

# Test 5: Process with agent (complex example)
echo "5️⃣  Processing text with agent_mother (Complex)..."
echo '   POST $BASE_URL/agents/agent_mother'
echo '   Body: {"input": "John Smith and Jane Doe..."}'
echo ""
curl -s -X POST "$BASE_URL/agents/agent_mother" \
  -H "Content-Type: application/json" \
  -d '{"input": "John Smith and Jane Doe traveled to Paris, France last week. They met with Marie Curie at the Eiffel Tower and discussed plans to visit New York City next month. Robert Johnson from London will join them at Central Park."}' | python3 -m json.tool
echo ""
echo "-----------------------------------------------------------------------"
echo ""

echo "======================================================================="
echo "✅ All tests completed!"
echo "======================================================================="

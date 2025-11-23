#!/bin/bash

# Simple test for the attention_filter agent
echo "🧪 Testing Simplified Attention Filter Agent"
echo "==========================================="
echo ""

# Test 1: Elon Musk Mars announcement (should process)
echo "Test 1: Elon Musk Mars announcement"
curl -X POST http://localhost:8080/agents/attention_filter \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Elon Musk said SpaceX will go to Mars in 2030",
    "model": "gemini-2.0-flash"
  }' | python3 -m json.tool

echo ""
echo "---"

# Test 2: Short spam (should skip)
echo "Test 2: Short spam content"
curl -X POST http://localhost:8080/agents/attention_filter \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Buy now!",
    "model": "gemini-2.0-flash"
  }' | python3 -m json.tool

echo ""
echo "---"

# Test 3: Meeting note (should process)
echo "Test 3: Meeting note"
curl -X POST http://localhost:8080/agents/attention_filter \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Meeting with Sarah Chen about the API project next Tuesday at 3pm",
    "model": "gpt-oss-20b"
  }' | python3 -m json.tool

echo ""
echo "✅ Tests complete!"
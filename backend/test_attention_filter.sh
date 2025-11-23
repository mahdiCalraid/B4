#!/bin/bash

# Test script for attention_filter agent
# This script tests various scenarios with the attention filter agent

echo "🧪 Testing Attention Filter Agent"
echo "=================================="
echo ""

# Base URL
BASE_URL="http://localhost:8080"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local test_name="$1"
    local endpoint="$2"
    local data="$3"

    echo -e "${BLUE}Test: ${test_name}${NC}"
    echo "Request: $data"
    echo "Response:"

    curl -X POST "${BASE_URL}${endpoint}" \
        -H "Content-Type: application/json" \
        -d "$data" \
        -s | python3 -m json.tool

    echo ""
    echo "---"
    echo ""
}

# Check if server is running
echo "Checking server health..."
if ! curl -s "${BASE_URL}/health" > /dev/null; then
    echo -e "${RED}❌ Server is not running!${NC}"
    echo "Please start the server with: cd /Users/ed/King/B4/backend && sh run.sh"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test 1: High-relevance tech news (Should process)
test_endpoint \
    "High-relevance tech news about Elon Musk" \
    "/agents/attention_filter" \
    '{
        "input": "Elon Musk announced that SpaceX will launch Starship to Mars in 2030, marking a major milestone in space exploration.",
        "model": "regex"
    }'

# Test 2: Meeting with known person (Should process)
test_endpoint \
    "Personal meeting with Sarah" \
    "/agents/attention_filter" \
    '{
        "input": "Meeting with Sarah Chen about the API v2 Project next Tuesday at 3pm",
        "model": "regex"
    }'

# Test 3: AI/OpenAI news (Should process)
test_endpoint \
    "OpenAI GPT-5 announcement" \
    "/agents/attention_filter" \
    '{
        "input": "OpenAI CEO Sam Altman revealed GPT-5 will be released in March 2025 with revolutionary reasoning capabilities",
        "model": "regex"
    }'

# Test 4: Low-relevance content (Should skip)
test_endpoint \
    "Random promotional content" \
    "/agents/attention_filter" \
    '{
        "input": "Buy now! Limited time offer on kitchen appliances. 50% off all items!",
        "model": "regex"
    }'

# Test 5: Too short content (Should skip)
test_endpoint \
    "Very short input" \
    "/agents/attention_filter" \
    '{
        "input": "Hello",
        "model": "regex"
    }'

# Test 6: Complex JSON input with metadata
test_endpoint \
    "JSON input with metadata" \
    "/agents/attention_filter" \
    '{
        "input": "{\"text\": \"Breaking: SpaceX successfully tested the new Raptor engine for Mars mission\", \"metadata\": {\"source\": \"techcrunch\", \"timestamp\": \"2024-11-16T10:00:00Z\"}}",
        "model": "regex"
    }'

# Test 7: Borderline case - use AI escalation
test_endpoint \
    "Borderline relevance - triggers AI" \
    "/agents/attention_filter" \
    '{
        "input": "The technology sector saw mixed results today with some companies reporting growth",
        "model": "gpt-oss-20b"
    }'

# Test 8: Multiple known entities
test_endpoint \
    "Multiple entities mentioned" \
    "/agents/attention_filter" \
    '{
        "input": "Elon Musk met with Sam Altman to discuss the future of AI at OpenAI headquarters. They talked about GPT-5 and Mars colonization.",
        "model": "regex"
    }'

echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "Summary:"
echo "- Tests 1-3, 6, 8 should show 'should_process': true"
echo "- Tests 4-5 should show 'should_process': false"
echo "- Test 7 should use AI for deeper analysis"
echo ""
echo "Check the responses above to verify the agent is working correctly!"
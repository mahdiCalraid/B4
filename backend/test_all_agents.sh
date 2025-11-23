#!/bin/bash

# Test all 9 agents in the B4 waterfall pipeline
echo "🌊 B4 WATERFALL PIPELINE - TESTING ALL AGENTS"
echo "=============================================="
echo ""

# Test input
INPUT="Elon Musk announced that SpaceX will launch Starship to Mars in 2030"

# Base URL
BASE_URL="http://localhost:8080"

# Function to test an agent
test_agent() {
    local agent_id="$1"
    local stage="$2"
    local description="$3"

    echo "──────────────────────────────────────────────"
    echo "🤖 $stage: $agent_id"
    echo "   $description"
    echo "──────────────────────────────────────────────"

    # Make the API call
    response=$(curl -X POST "${BASE_URL}/agents/${agent_id}" \
        -H "Content-Type: application/json" \
        -d "{\"input\": \"${INPUT}\", \"model\": \"gemini-2.0-flash\"}" \
        -s 2>/dev/null)

    # Check if response is valid JSON
    if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        # Extract key information based on agent
        if echo "$response" | grep -q '"success": true'; then
            echo "   ✅ Success"

            case "$agent_id" in
                "attention_filter")
                    should_process=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('should_process'))" 2>/dev/null)
                    relevance=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('relevance_score'))" 2>/dev/null)
                    echo "   Should Process: $should_process"
                    echo "   Relevance Score: $relevance"
                    ;;
                "entity_extractor")
                    total=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('total_entities'))" 2>/dev/null)
                    echo "   Total Entities: $total"
                    ;;
                "concept_sentiment")
                    sentiment=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('overall_sentiment', {}).get('sentiment'))" 2>/dev/null)
                    echo "   Overall Sentiment: $sentiment"
                    ;;
                "memory_writer")
                    records=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('memory_records', [])))" 2>/dev/null)
                    echo "   Memory Records Created: $records"
                    ;;
                *)
                    # For other agents, just show that they succeeded
                    echo "   Data returned successfully"
                    ;;
            esac
        else
            echo "   ❌ Failed"
            echo "$response" | python3 -m json.tool 2>/dev/null | head -5
        fi
    else
        echo "   ❌ Error: Invalid response"
        echo "   $response" | head -1
    fi

    echo ""
}

# Check if server is running
echo "Checking server health..."
if ! curl -s "${BASE_URL}/health" > /dev/null; then
    echo "❌ Server is not running!"
    echo "Please start the server with: cd /Users/ed/King/B4/backend && sh run.sh"
    exit 1
fi
echo "✅ Server is running"
echo ""

echo "Test Input: \"$INPUT\""
echo ""

# Test all agents in order
test_agent "attention_filter" "Stage 1: ATTENTION" "Filter irrelevant content"
test_agent "context_builder" "Stage 2: PERCEPTION" "Build temporal and spatial context"
test_agent "entity_extractor" "Stage 3: COMPREHENSION" "Extract entities"
test_agent "event_action" "Stage 3: COMPREHENSION" "Detect events and actions"
test_agent "concept_sentiment" "Stage 3: COMPREHENSION" "Analyze concepts and sentiment"
test_agent "entity_resolver" "Stage 4: CONSOLIDATION" "Resolve and enrich entities"
test_agent "hypothesis_generator" "Stage 4: CONSOLIDATION" "Generate insights"
test_agent "memory_prioritizer" "Stage 5: INTEGRATION" "Prioritize for storage"
test_agent "memory_writer" "Stage 5: INTEGRATION" "Format for database"

echo "=============================================="
echo "✨ All agents tested!"
echo ""
echo "Note: Each agent was tested independently."
echo "In production, they would pass enriched data through the pipeline."
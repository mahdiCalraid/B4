#!/usr/bin/env python3
"""Quick summary test of all 9 B4 agents."""

import json
import subprocess

def test_agent(agent_id):
    """Test a single agent and return status."""
    cmd = [
        'curl', '-X', 'POST',
        f'http://localhost:8080/agents/{agent_id}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            "input": "Elon Musk announced SpaceX will go to Mars in 2030",
            "model": "gemini-2.0-flash"
        }),
        '-s'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get('success') and response.get('data'):
                # Check if data has content (not empty dict)
                if len(str(response.get('data', {}))) > 10:
                    return "✅ Working"
                else:
                    return "⚠️ Empty data"
            else:
                return "❌ Failed"
        else:
            return "❌ Error"
    except Exception as e:
        return f"❌ Exception: {str(e)[:20]}"

def main():
    print("🌊 B4 WATERFALL PIPELINE - AGENT STATUS CHECK")
    print("=" * 50)

    agents = [
        ("attention_filter", "Stage 1: ATTENTION"),
        ("context_builder", "Stage 2: PERCEPTION"),
        ("entity_extractor", "Stage 3: COMPREHENSION"),
        ("event_action", "Stage 3: COMPREHENSION"),
        ("concept_sentiment", "Stage 3: COMPREHENSION"),
        ("entity_resolver", "Stage 4: CONSOLIDATION"),
        ("hypothesis_generator", "Stage 4: CONSOLIDATION"),
        ("memory_prioritizer", "Stage 5: INTEGRATION"),
        ("memory_writer", "Stage 5: INTEGRATION")
    ]

    working = 0
    for agent_id, stage in agents:
        status = test_agent(agent_id)
        print(f"{status} {agent_id:20} ({stage})")
        if "✅" in status:
            working += 1

    print("=" * 50)
    print(f"Summary: {working}/9 agents working")

    if working == 9:
        print("🎉 All agents are operational!")
    elif working > 6:
        print("👍 Most agents are working")
    else:
        print("⚠️ Some agents may need attention")

if __name__ == "__main__":
    main()
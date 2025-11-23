#!/usr/bin/env python3
"""
Direct test of the simplified attention_filter agent.
This tests the agent as a standard agent like agent_mother.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_attention_filter():
    """Test the simplified attention filter agent"""

    print("🧪 Testing Simplified Attention Filter Agent")
    print("=" * 50)

    # Import the agent loader
    from agents.agent_loader import AgentLoader

    # Initialize loader
    loader = AgentLoader()

    # Load the attention_filter agent
    print("\n📦 Loading attention_filter agent...")
    try:
        agent = loader.load_agent('attention_filter')
        print("✅ Agent loaded successfully")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Agent Path: {agent.agent_path}")
    except Exception as e:
        print(f"❌ Failed to load agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test cases
    test_cases = [
        {
            "name": "Elon Musk Mars announcement",
            "input": "Elon Musk announced SpaceX will go to Mars in 2030",
            "model": "gpt-oss-20b"
        },
        {
            "name": "Meeting with Sarah",
            "input": "Meeting with Sarah Chen about the API project next week at 2pm in conference room B",
            "model": "gemini-2.0-flash"
        },
        {
            "name": "OpenAI GPT-5 news",
            "input": "OpenAI's Sam Altman revealed GPT-5 will have revolutionary reasoning capabilities when it launches in March 2025",
            "model": "gpt-oss-20b"
        },
        {
            "name": "Random spam",
            "input": "Click here for amazing deals!",
            "model": "gpt-oss-20b"
        },
        {
            "name": "Too short",
            "input": "Hi there",
            "model": "gpt-oss-20b"
        }
    ]

    # Run tests
    print("\n🏃 Running test cases...")
    print("-" * 50)

    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"   Input: \"{test['input'][:60]}...\"" if len(test['input']) > 60 else f"   Input: \"{test['input']}\"")
        print(f"   Model: {test['model']}")

        try:
            # Process with the agent
            result = await agent.process(
                input_data=test['input'],
                model=test['model']
            )

            # Display results
            if isinstance(result, dict):
                data = result.get('data', result)
            else:
                data = result

            print(f"\n   Results:")
            print(f"   - Should process: {data.get('should_process')}")
            print(f"   - Relevance: {data.get('relevance_score')}")
            print(f"   - Importance: {data.get('importance_score')}")

            if data.get('detected_domains'):
                print(f"   - Domains: {data['detected_domains']}")

            if data.get('entity_hints'):
                print(f"   - Entities found:")
                for entity in data['entity_hints'][:3]:  # Show first 3
                    print(f"       • {entity.get('text')} ({entity.get('type')})")

            if data.get('information_signals'):
                print(f"   - Signals: {data['information_signals']}")

            if data.get('skip_reason'):
                print(f"   - Skip reason: {data['skip_reason']}")

            if data.get('reasoning'):
                print(f"   - Reasoning: {data['reasoning'][:100]}...")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_attention_filter())
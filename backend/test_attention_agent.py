#!/usr/bin/env python3
"""
Direct test of the attention_filter agent with database integration.
Run this to verify the agent works correctly with pattern matching and entity cache.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_attention_filter():
    """Test the attention filter agent directly"""

    print("🧪 Testing Attention Filter Agent")
    print("=" * 50)

    # Import the agent
    from agents.agent_loader import AgentLoader

    # Initialize loader
    loader = AgentLoader()

    # Load the attention_filter agent
    print("\n📦 Loading attention_filter agent...")
    try:
        agent = loader.load_agent('attention_filter')
        print("✅ Agent loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load agent: {e}")
        return

    # Initialize if it's our custom agent
    if hasattr(agent, 'initialize'):
        print("🔄 Initializing agent with database...")
        await agent.initialize()

    # Test cases
    test_cases = [
        {
            "name": "Elon Musk Mars announcement",
            "input": "Elon Musk announced SpaceX will go to Mars in 2030",
            "expected": "should_process: true (known entity detected)"
        },
        {
            "name": "Meeting with Sarah",
            "input": "Meeting with Sarah Chen about the API project next week",
            "expected": "should_process: true (personal + known person)"
        },
        {
            "name": "GPT-5 news",
            "input": "OpenAI's Sam Altman revealed GPT-5 capabilities",
            "expected": "should_process: true (tech + multiple entities)"
        },
        {
            "name": "Random spam",
            "input": "Click here for amazing deals on shoes!",
            "expected": "should_process: false (low relevance)"
        },
        {
            "name": "Too short",
            "input": "Hi",
            "expected": "should_process: false (too short)"
        }
    ]

    # Run tests
    print("\n🏃 Running test cases...")
    print("-" * 50)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input: '{test['input']}'")
        print(f"Expected: {test['expected']}")

        try:
            # Process with the agent
            result = await agent.process(
                input_data=test['input'],
                model='regex'  # Use pattern matching only for speed
            )

            # Display key results
            print(f"Result:")
            print(f"  - Should process: {result.get('should_process')}")
            print(f"  - Relevance: {result.get('relevance_score')}")
            print(f"  - Importance: {result.get('importance_score')}")

            if result.get('known_entity_hints'):
                print(f"  - Detected entities: {result['known_entity_hints']}")

            if result.get('detected_domains'):
                print(f"  - Domains: {result['detected_domains']}")

            if result.get('skip_reason'):
                print(f"  - Skip reason: {result['skip_reason']}")

            # Check if result matches expectation
            if "true" in test['expected'].lower():
                if result.get('should_process'):
                    print("✅ PASS")
                else:
                    print("❌ FAIL - Expected to process but didn't")
            else:
                if not result.get('should_process'):
                    print("✅ PASS")
                else:
                    print("❌ FAIL - Expected to skip but didn't")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    # Test with AI escalation
    print("\n" + "=" * 50)
    print("📈 Testing AI Escalation (borderline case)...")

    borderline_input = "Technology companies are doing interesting things"
    print(f"Input: '{borderline_input}'")

    try:
        # First with pattern matching only
        result_regex = await agent.process(
            input_data=borderline_input,
            model='regex'
        )
        print(f"\nWith regex only:")
        print(f"  - Should process: {result_regex.get('should_process')}")
        print(f"  - Relevance: {result_regex.get('relevance_score')}")

        # Then with AI escalation
        result_ai = await agent.process(
            input_data=borderline_input,
            model='gpt-oss-20b'
        )
        print(f"\nWith AI escalation:")
        print(f"  - Should process: {result_ai.get('should_process')}")
        print(f"  - Relevance: {result_ai.get('relevance_score')}")
        print(f"  - Processing method: {result_ai.get('processing_method')}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Show cache stats
    if hasattr(agent, 'processor'):
        print("\n" + "=" * 50)
        print("📊 Entity Cache Statistics:")
        cache = agent.processor.entity_cache
        print(f"  - Entities in cache: {len(cache.get_entity_ids())}")
        print(f"  - Cache initialized: {cache.initialized}")

        # Show some cached entities
        if cache.top_entities:
            print(f"\n  Top cached entities:")
            for entity in cache.top_entities[:5]:
                print(f"    - {entity['title']} ({entity['type']})")

    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_attention_filter())
#!/usr/bin/env python3
"""Test waterfall with fixed attention filter."""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_waterfall():
    """Test the waterfall pipeline with logging."""

    print("🌊 Testing Waterfall Pipeline with Fixed Attention Filter")
    print("=" * 60)

    # Import required components
    from agents.agent_loader import get_loader
    from agents.waterfall.simple_orchestrator import SimpleWaterfallOrchestrator

    # Initialize the orchestrator
    print("\n🎭 Initializing Waterfall Orchestrator...")
    orchestrator = SimpleWaterfallOrchestrator()

    # Test input
    test_input = "Elon Musk announced that SpaceX will launch Starship to Mars in 2030"

    print(f"\n📝 Test Input: '{test_input}'")
    print("-" * 60)

    try:
        # Process through single agent first to verify it works
        print("\n📤 Testing attention_filter agent alone...")
        loader = get_loader()
        agent = loader.load_agent('attention_filter')

        result = await agent.process(
            input_data=test_input,
            model='gemini-2.0-flash'
        )

        print(f"✅ Attention filter result:")
        print(f"  - Should process: {result.get('should_process')}")
        print(f"  - Relevance: {result.get('relevance_score')}")
        print(f"  - Importance: {result.get('importance_score')}")

        if result.get('entity_hints'):
            print(f"  - Detected entities: {len(result.get('entity_hints'))} entities")

        # Now test orchestrator
        print("\n📤 Testing waterfall orchestrator...")
        pipeline_result = await orchestrator.process(test_input)

        print(f"\n✅ Pipeline complete!")
        print(f"  - Stage 1 result: {pipeline_result.get('stage_1', {}).get('should_process')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_waterfall())
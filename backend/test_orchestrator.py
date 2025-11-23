#!/usr/bin/env python3
"""
Test the waterfall orchestrator with logging.
Shows complete pipeline flow with decision making.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_orchestrator():
    """Test the orchestrator with different inputs"""

    print("🌊 WATERFALL ORCHESTRATOR TEST")
    print("=" * 60)

    from agents.waterfall.simple_orchestrator import SimpleWaterfallOrchestrator

    # Create orchestrator
    orchestrator = SimpleWaterfallOrchestrator()

    # Test cases
    test_cases = [
        {
            "name": "Tech News - Should Process",
            "input": "Elon Musk announced SpaceX will launch Starship to Mars in 2030",
            "expected": "Should pass through all stages"
        },
        {
            "name": "Short Spam - Should Skip",
            "input": "Buy now!",
            "expected": "Should be filtered at attention stage"
        },
        {
            "name": "Meeting Note - Should Process",
            "input": "Meeting with Sarah Chen next Tuesday about API project in conference room B",
            "expected": "Should pass through all stages"
        }
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"📝 TEST: {test['name']}")
        print(f"   Input: {test['input']}")
        print(f"   Expected: {test['expected']}")
        print("-" * 60)

        try:
            # Process through orchestrator
            result = await orchestrator.process(
                test["input"],
                {"test_name": test["name"]}
            )

            # Show results
            print(f"\n📊 RESULTS:")
            print(f"   Processed: {result['processed']}")
            print(f"   Stages Completed: {result['stages_completed']}")

            # Show each stage result
            for stage, stage_result in result["results"].items():
                print(f"\n   📍 {stage}:")
                if isinstance(stage_result, dict):
                    for key, value in list(stage_result.items())[:5]:  # Show first 5 fields
                        if key == "entity_hints" and isinstance(value, list):
                            print(f"      {key}: {len(value)} entities found")
                        elif isinstance(value, (str, int, float, bool)):
                            print(f"      {key}: {value}")
                        elif isinstance(value, list):
                            print(f"      {key}: {len(value)} items")

            # Show trace summary
            print(f"\n   📜 Processing Trace: {len(result.get('trace', []))} steps recorded")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Orchestrator test complete!")

    # Show the final waterfall report
    from agents.general_codes.waterfall_logger import get_waterfall_logger
    logger = get_waterfall_logger()

    print("\n" + "=" * 60)
    print("📋 FINAL WATERFALL REPORT")
    print("=" * 60)
    print(logger.format_waterfall_report())

if __name__ == "__main__":
    import os
    # Enable debug logging
    os.environ["LOG_LEVEL"] = "INFO"

    print("Starting Waterfall Orchestrator Test")
    print("This demonstrates the complete pipeline with logging\n")

    asyncio.run(test_orchestrator())
#!/usr/bin/env python3
"""
Test the waterfall logging system with multiple agents.
Shows how logging tracks data flow through the pipeline.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment for detailed logging
import os
os.environ["LOG_LEVEL"] = "DEBUG"

async def test_waterfall_with_logging():
    """Test multiple agents with waterfall logging"""

    print("🌊 WATERFALL LOGGING TEST")
    print("=" * 60)

    # Import logger and agent loader
    from agents.general_codes.waterfall_logger import get_waterfall_logger
    from agents.agent_loader import AgentLoader

    # Get the logger
    logger = get_waterfall_logger()

    # Initialize loader
    loader = AgentLoader()

    # Test input
    test_input = "Elon Musk announced that SpaceX will launch Starship to Mars in 2030"

    # Start pipeline logging
    logger.start_processing(test_input, {"source": "test", "timestamp": "2024-11-18"})

    print("\n📊 Processing through agents with logging...")
    print("-" * 60)

    # Test 1: attention_filter agent
    print("\n1️⃣ ATTENTION FILTER AGENT")
    try:
        attention_agent = loader.load_agent('attention_filter')
        result1 = await attention_agent.process(
            input_data=test_input,
            model='gpt-oss-20b'
        )
        print(f"   Result: {json.dumps(result1, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: agent_mother
    print("\n2️⃣ AGENT MOTHER")
    try:
        mother_agent = loader.load_agent('agent_mother')
        result2 = await mother_agent.process(
            input_data=test_input,
            model='gemini-2.0-flash'
        )
        print(f"   Result: {json.dumps(result2, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: test_agent (if exists)
    print("\n3️⃣ TEST AGENT")
    try:
        test_agent = loader.load_agent('test_agent')
        result3 = await test_agent.process(
            input_data=test_input,
            model='gpt-oss-20b'
        )
        print(f"   Result: {json.dumps(result3, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Complete pipeline
    logger.pipeline_complete()

    # Print the waterfall report
    print("\n" + "=" * 60)
    print("📜 WATERFALL PROCESSING REPORT")
    print("=" * 60)
    report = logger.format_waterfall_report()
    print(report)

    # Show recent logs
    print("\n" + "=" * 60)
    print("📝 RECENT LOG ENTRIES")
    print("=" * 60)
    recent_logs = logger.get_recent_logs(20)
    for log in recent_logs[-10:]:  # Show last 10
        timestamp = log.get('timestamp', '')[:19]  # Trim microseconds
        event = log.get('event', '')
        agent = log.get('agent', '')

        if event == 'agent_start':
            print(f"{timestamp} | START | {agent} | Model: {log.get('model', 'default')}")
        elif event == 'agent_step':
            print(f"{timestamp} | STEP  | {agent} | {log.get('step', '')}")
        elif event == 'agent_result':
            print(f"{timestamp} | RESULT| {agent} | {log.get('summary', '')}")
        elif event == 'agent_error':
            print(f"{timestamp} | ERROR | {agent} | {log.get('error', '')}")
        elif event == 'pipeline_start':
            print(f"{timestamp} | PIPELINE START | Input: {log.get('input', '')[:50]}...")
        elif event == 'pipeline_complete':
            print(f"{timestamp} | PIPELINE COMPLETE | {log.get('trace_length', 0)} steps")

if __name__ == "__main__":
    print("🚀 Starting Waterfall Logging Test")
    print("   This shows how logging tracks data through agents")
    print("")

    asyncio.run(test_waterfall_with_logging())
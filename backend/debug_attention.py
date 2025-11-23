#!/usr/bin/env python3
"""Debug script to understand why attention_filter returns empty data."""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def debug_attention():
    """Debug the attention filter agent."""

    print("🔍 Debugging Attention Filter Agent")
    print("=" * 50)

    # Import the loader
    from agents.agent_loader import get_loader

    # Load the agent
    loader = get_loader()
    agent = loader.load_agent('attention_filter')

    # Check what the agent has loaded
    print("\n📋 Agent Configuration:")
    print(f"  Agent ID: {agent.agent_id}")
    print(f"  Prompt Template Length: {len(agent.prompt_template)} chars")
    print(f"  Output Schema: {json.dumps(agent.output_schema, indent=2) if agent.output_schema else 'None'}")
    print(f"  Config: {agent.config}")

    # Check if pydantic model is created
    print("\n🏗️ Pydantic Model:")
    response_model = agent._create_pydantic_model()
    if response_model:
        print(f"  Model Name: {response_model.__name__}")
        print(f"  Model Fields: {response_model.model_fields}")
    else:
        print("  No model created!")

    # Test input
    test_input = "Elon Musk announced SpaceX will go to Mars in 2030"

    print(f"\n🧪 Testing with input: '{test_input}'")
    print("-" * 50)

    # Try to process with model='regex' (pattern matching only)
    print("\n📤 Processing with model='regex'...")
    try:
        result = await agent.process(
            input_data=test_input,
            model='regex'
        )
        print(f"✅ Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Check the formatted prompt
    print("\n📝 Formatted Prompt Preview:")
    formatted_prompt = agent.prompt_template
    if "{input_data}" in formatted_prompt:
        formatted_prompt = formatted_prompt.format(input_data=test_input)
    elif "{input}" in formatted_prompt:
        formatted_prompt = formatted_prompt.format(input=test_input)
    print(formatted_prompt[:500] + "..." if len(formatted_prompt) > 500 else formatted_prompt)

if __name__ == "__main__":
    asyncio.run(debug_attention())
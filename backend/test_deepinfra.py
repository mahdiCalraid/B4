"""
Test script for DeepInfra API connection.

This script tests the DeepInfra gpt-oss-20b model both directly via curl
and through the B4 agent system.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


async def test_deepinfra_direct():
    """Test DeepInfra API directly using their Python client."""
    print("=" * 70)
    print("🧪 Test 1: DeepInfra Direct API Call")
    print("=" * 70)
    print()

    api_key = os.getenv("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_TOKEN")

    if not api_key:
        print("❌ DEEPINFRA_API_KEY not set in environment")
        print()
        print("To get your API key:")
        print("1. Go to https://deepinfra.com")
        print("2. Sign up or log in")
        print("3. Go to https://deepinfra.com/dash/api_keys")
        print("4. Create a new API key")
        print("5. Export it: export DEEPINFRA_API_KEY='your_key_here'")
        print()
        return False

    print(f"✅ API Key found: {api_key[:20]}...")
    print()

    # Test with OpenAI-compatible interface
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url="https://api.deepinfra.com/v1/openai",
            api_key=api_key
        )

        print("📤 Sending test request to DeepInfra...")
        print("   Model: openai/gpt-oss-20b")
        print("   Input: 'Hello, world!'")
        print()

        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": "Say hello in one sentence"}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print("✅ DeepInfra API Response:")
        print(f"   {result}")
        print()
        return True

    except Exception as e:
        print(f"❌ Error calling DeepInfra API: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_deepinfra_agent():
    """Test DeepInfra through B4 agent system."""
    print("=" * 70)
    print("🧪 Test 2: DeepInfra via B4 Agent System")
    print("=" * 70)
    print()

    api_key = os.getenv("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_TOKEN")

    if not api_key:
        print("⚠️  Skipping (no API key)")
        print()
        return False

    try:
        from modules.agents.deepinfra_agent import DeepInfraAgent

        print("📦 Creating DeepInfraAgent...")
        agent = DeepInfraAgent(
            model_name="openai/gpt-oss-20b"
        )
        print("✅ Agent created successfully")
        print()

        print("📤 Testing text generation...")
        result = await agent.generate(
            prompt="What is 2+2? Answer in one sentence.",
            system_prompt="You are a helpful assistant."
        )
        print(f"✅ Response: {result}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_mother_with_deepinfra():
    """Test agent_mother with gpt-oss-20b model."""
    print("=" * 70)
    print("🧪 Test 3: Agent Mother with gpt-oss-20b")
    print("=" * 70)
    print()

    api_key = os.getenv("DEEPINFRA_API_KEY") or os.getenv("DEEPINFRA_TOKEN")

    if not api_key:
        print("⚠️  Skipping (no API key)")
        print()
        return False

    try:
        from agents.agent_loader import AgentLoader

        print("📦 Loading agent_mother...")
        loader = AgentLoader()
        agent = loader.load_agent("agent_mother")
        print("✅ Agent loaded")
        print()

        test_input = "Elon Musk visited SpaceX headquarters in Hawthorne, California."

        print(f"📤 Processing with gpt-oss-20b...")
        print(f"   Input: {test_input}")
        print()

        result = await agent.process(
            input_data=test_input,
            model="gpt-oss-20b"
        )

        print("✅ Result:")
        import json
        print(json.dumps(result, indent=2))
        print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DeepInfra Integration Test Suite" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = []

    # Test 1: Direct API
    success = await test_deepinfra_direct()
    results.append(("Direct DeepInfra API", success))

    # Test 2: DeepInfra Agent
    success = await test_deepinfra_agent()
    results.append(("DeepInfraAgent", success))

    # Test 3: Agent Mother with model selection
    success = await test_agent_mother_with_deepinfra()
    results.append(("Agent Mother + gpt-oss-20b", success))

    # Summary
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print()

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")

    print()

    all_passed = all(success for _, success in results if success is not None)

    if all_passed:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed or were skipped")
        print()
        print("Make sure DEEPINFRA_API_KEY is set:")
        print("  export DEEPINFRA_API_KEY='your_key_here'")

    print()


if __name__ == "__main__":
    asyncio.run(main())

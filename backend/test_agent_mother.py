"""
Test script for agent_mother using direct function calling.

This script tests the agent system by directly calling the agent
without going through the HTTP API.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from agents.agent_loader import AgentLoader


async def test_agent_mother():
    """Test the mother agent with sample input."""

    print("=" * 70)
    print("🧪 Testing Agent Mother (Direct Function Call)")
    print("=" * 70)
    print()

    # Create loader
    print("📦 Loading agent...")
    loader = AgentLoader()

    # List available agents
    print("\n📋 Available agents:")
    agents = loader.list_agents()
    for agent_id, info in agents.items():
        print(f"  - {agent_id}")
    print()

    # Load mother agent
    try:
        agent = loader.load_agent("agent_mother")
        print("✅ Agent loaded successfully!")
        print()

        # Print agent info
        print("ℹ️  Agent Information:")
        info = agent.get_info()
        print(f"  Name: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Role: {info['role']}")
        print(f"  Provider: {info['provider']['provider']}")
        print(f"  Model: {info['provider']['model']}")
        print()

        # Test input
        test_input = """
        John Smith and Jane Doe traveled to Paris, France last week.
        They met with Marie Curie at the Eiffel Tower and discussed plans
        to visit New York City next month. Robert Johnson from London
        will join them at Central Park.
        """

        print("📝 Test Input:")
        print(test_input.strip())
        print()

        # Process
        print("🤖 Processing with agent...")
        result = await agent.process(test_input)
        print()

        # Display results
        print("✨ Results:")
        print("=" * 70)

        if "people" in result:
            print(f"\n👥 People found ({len(result['people'])}):")
            for person in result['people']:
                print(f"  - {person.get('full_name', 'N/A')}")
                if person.get('first_name'):
                    print(f"    First: {person['first_name']}")
                if person.get('last_name'):
                    print(f"    Last: {person['last_name']}")

        if "places" in result:
            print(f"\n📍 Places found ({len(result['places'])}):")
            for place in result['places']:
                print(f"  - {place.get('name', 'N/A')} ({place.get('type', 'unknown')})")

        print()
        print("=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_agent_mother())
    sys.exit(0 if success else 1)

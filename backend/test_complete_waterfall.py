#!/usr/bin/env python3
"""Test the complete B4 waterfall pipeline with all 9 agents."""

import asyncio
import json
from pathlib import Path
import sys
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_complete_waterfall():
    """Test all 9 agents in the waterfall pipeline."""

    print("🌊 B4 COMPLETE WATERFALL PIPELINE TEST")
    print("=" * 70)
    print("Testing all 9 agents across 5 stages")
    print("=" * 70)

    # Import the agent loader
    from agents.agent_loader import get_loader

    # Test input
    test_input = "Elon Musk announced that SpaceX will launch Starship to Mars in 2030, marking a historic milestone for humanity's space exploration ambitions."

    print(f"\n📝 Test Input:")
    print(f"'{test_input}'")
    print("\n" + "=" * 70)

    # Initialize loader
    loader = get_loader()

    # Track results through the pipeline
    pipeline_results = {}

    # Define the agents in order
    agents = [
        ("attention_filter", "Stage 1: ATTENTION", "Filter irrelevant content"),
        ("context_builder", "Stage 2: PERCEPTION", "Build temporal and spatial context"),
        ("entity_extractor", "Stage 3: COMPREHENSION", "Extract entities"),
        ("event_action", "Stage 3: COMPREHENSION", "Detect events and actions"),
        ("concept_sentiment", "Stage 3: COMPREHENSION", "Analyze concepts and sentiment"),
        ("entity_resolver", "Stage 4: CONSOLIDATION", "Resolve and enrich entities"),
        ("hypothesis_generator", "Stage 4: CONSOLIDATION", "Generate insights and predictions"),
        ("memory_prioritizer", "Stage 5: INTEGRATION", "Prioritize for storage"),
        ("memory_writer", "Stage 5: INTEGRATION", "Format for database storage")
    ]

    # Process through each agent
    current_input = test_input
    for agent_id, stage, description in agents:
        print(f"\n{'─' * 70}")
        print(f"🤖 {stage}")
        print(f"   Agent: {agent_id}")
        print(f"   Role: {description}")
        print(f"{'─' * 70}")

        try:
            # Load the agent
            agent = loader.load_agent(agent_id)

            # Process the input
            print(f"   ⏳ Processing...")
            result = await agent.process(
                input_data=current_input,
                model='gemini-2.0-flash'  # Use a consistent model
            )

            # Store the result
            pipeline_results[agent_id] = result

            # Display key results based on agent type
            if agent_id == "attention_filter":
                print(f"   ✅ Should Process: {result.get('should_process')}")
                print(f"   📊 Relevance Score: {result.get('relevance_score')}")
                print(f"   📈 Importance Score: {result.get('importance_score')}")
                if not result.get('should_process'):
                    print(f"   ⚠️ Skip Reason: {result.get('skip_reason')}")
                    print("\n🛑 Content filtered out - stopping pipeline")
                    break

            elif agent_id == "context_builder":
                temporal = result.get('temporal_context', {})
                spatial = result.get('spatial_context', {})
                print(f"   🕐 Temporal Scope: {temporal.get('temporal_scope')}")
                print(f"   📍 Locations: {len(spatial.get('locations', []))} found")
                print(f"   🔗 Related Memories: {len(result.get('related_memories', []))} simulated")

            elif agent_id == "entity_extractor":
                print(f"   👤 People: {len(result.get('people', []))} found")
                print(f"   🏢 Organizations: {len(result.get('organizations', []))} found")
                print(f"   📍 Locations: {len(result.get('locations', []))} found")
                print(f"   🔢 Total Entities: {result.get('total_entities')}")

            elif agent_id == "event_action":
                print(f"   📅 Events: {len(result.get('events', []))} detected")
                print(f"   🎯 Actions: {len(result.get('actions', []))} identified")
                timeline = result.get('timeline', {})
                print(f"   ⏰ Timeline: Past({timeline.get('past_events', 0)}), Present({timeline.get('present_events', 0)}), Future({timeline.get('future_events', 0)})")

            elif agent_id == "concept_sentiment":
                sentiment = result.get('overall_sentiment', {})
                print(f"   😊 Overall Sentiment: {sentiment.get('sentiment')} (score: {sentiment.get('score')})")
                print(f"   💡 Key Concepts: {len(result.get('key_concepts', []))} identified")
                print(f"   🎨 Themes: {len(result.get('themes', []))} found")

            elif agent_id == "entity_resolver":
                print(f"   🔍 Resolved Entities: {len(result.get('resolved_entities', []))}")
                summary = result.get('resolution_summary', {})
                print(f"   📊 Resolution Rate: {summary.get('resolved_count', 0)}/{summary.get('total_mentions', 0)}")
                print(f"   🎯 Confidence: {result.get('resolution_confidence')}")

            elif agent_id == "hypothesis_generator":
                print(f"   🔮 Predictions: {len(result.get('predictions', []))} generated")
                print(f"   💡 Hypotheses: {len(result.get('hypotheses', []))} formed")
                print(f"   🎯 Insights: {len(result.get('insights', []))} discovered")
                print(f"   ❓ Open Questions: {len(result.get('open_questions', []))}")

            elif agent_id == "memory_prioritizer":
                summary = result.get('priority_summary', {})
                print(f"   🎯 Critical: {summary.get('critical_count', 0)} memories")
                print(f"   ⭐ Important: {summary.get('important_count', 0)} memories")
                print(f"   📌 Useful: {summary.get('useful_count', 0)} memories")
                print(f"   📊 Average Importance: {summary.get('average_importance', 0):.2f}")

            elif agent_id == "memory_writer":
                print(f"   💾 Memory Records: {len(result.get('memory_records', []))} created")
                summary = result.get('storage_summary', {})
                print(f"   📚 By Type: Episodic({summary.get('by_type', {}).get('episodic', 0)}), Semantic({summary.get('by_type', {}).get('semantic', 0)})")
                print(f"   🔗 Total Connections: {summary.get('total_connections', 0)}")
                print(f"   ✅ Formation Confidence: {result.get('formation_confidence')}")

            # Pass enriched data to next agent
            if agent_id in ["attention_filter", "context_builder"]:
                # Early stages pass original input plus their analysis
                current_input = json.dumps({
                    "original_input": test_input,
                    agent_id: result
                })
            else:
                # Later stages get cumulative results
                current_input = json.dumps(pipeline_results)

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 70)
    print("📊 PIPELINE SUMMARY")
    print("=" * 70)

    successful_agents = [k for k in pipeline_results.keys()]
    print(f"✅ Successful Agents: {len(successful_agents)}/9")
    print(f"   Completed: {', '.join(successful_agents)}")

    if "memory_writer" in pipeline_results:
        print(f"\n🎉 PIPELINE COMPLETE!")
        print(f"   The input was successfully processed through all stages")
        print(f"   and converted into structured memory records.")
    elif "attention_filter" in pipeline_results:
        if not pipeline_results["attention_filter"].get("should_process"):
            print(f"\n⚠️ Pipeline stopped at attention filter (content not relevant)")
        else:
            print(f"\n⚠️ Pipeline partially completed")

    print("\n" + "=" * 70)
    print("✨ Test Complete!")

    return pipeline_results


if __name__ == "__main__":
    results = asyncio.run(test_complete_waterfall())

    # Optionally save results to file
    with open('waterfall_test_results.json', 'w') as f:
        # Convert results to serializable format
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            else:
                return obj

        json.dump(make_serializable(results), f, indent=2)
        print(f"\n📄 Results saved to waterfall_test_results.json")
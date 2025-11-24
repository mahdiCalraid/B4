import asyncio
import sys
import os

# Ensure we can import from current package
# When running as -m src.verify_workflow, .nodes should work

from .nodes import (
    PatternFilterNode,
    ContextBuilderNode,
    EntityExtractorNode,
    EventActionNode,
    ConceptSentimentNode,
    EntityResolverNode,
    HypothesisGeneratorNode,
    MemoryPrioritizerNode,
    MemoryWriterNode
)

async def run_workflow(text: str):
    print(f"Input: {text}")
    print("-" * 50)

    # 1. Attention (Configured with patterns)
    attention_config = {
        "patterns": [
            r"AI", r"artificial intelligence", r"machine learning",
            r"brain", r"neuroscience", r"memory",
            r"workflow", r"agent", r"automation",
            r"Elon Musk", r"SpaceX", r"Mars"
        ]
    }
    attention = PatternFilterNode(config=attention_config)
    res_1 = await attention.process({"text": text})
    print(f"Stage 1 (Attention): {res_1}")
    
    if not res_1["should_process"]:
        print("Skipping processing.")
        return

    # 2. Perception
    perception = ContextBuilderNode()
    res_2 = await perception.process({
        "text": text, 
        "detected_patterns": res_1["detected_patterns"]
    })
    print(f"Stage 2 (Perception): {res_2}")

    # 3. Comprehension (Parallel)
    extractor = EntityExtractorNode()
    event_action = EventActionNode()
    concept = ConceptSentimentNode()
    
    # Pass context from Stage 2
    comprehension_input = {
        "text": text,
        "context": res_2["context_frame"]
    }
    
    res_3_entities, res_3_events, res_3_concepts = await asyncio.gather(
        extractor.process(comprehension_input),
        event_action.process(comprehension_input),
        concept.process(comprehension_input)
    )
    print(f"Stage 3 (Comprehension):")
    print(f"  Entities: {res_3_entities}")
    print(f"  Events: {res_3_events}")
    print(f"  Concepts: {res_3_concepts}")

    # 4. Consolidation
    resolver = EntityResolverNode()
    hypothesis = HypothesisGeneratorNode()
    
    res_4_resolved = await resolver.process({"entities": res_3_entities["entities"]})
    res_4_hypothesis = await hypothesis.process({})
    
    print(f"Stage 4 (Consolidation):")
    print(f"  Resolved: {res_4_resolved}")
    print(f"  Hypothesis: {res_4_hypothesis}")

    # 5. Integration
    prioritizer = MemoryPrioritizerNode()
    writer = MemoryWriterNode()
    
    res_5_priority = await prioritizer.process({})
    res_5_write = await writer.process({"priority": res_5_priority["priority"]})
    
    print(f"Stage 5 (Integration):")
    print(f"  Priority: {res_5_priority}")
    print(f"  Write Status: {res_5_write}")
    print("-" * 50)

if __name__ == "__main__":
    # Test Case 1: Relevant
    asyncio.run(run_workflow("Elon Musk said we will be on Mars in 2030"))
    
    # Test Case 2: Irrelevant
    asyncio.run(run_workflow("I like eating apples for lunch"))

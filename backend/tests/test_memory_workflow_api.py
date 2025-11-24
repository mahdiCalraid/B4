import requests
import json
import time
import sys

BASE_URL = "http://localhost:8080"

def create_workflow():
    return {
        "id": "test-memory-workflow",
        "name": "Memory Workflow Test",
        "nodes": [
            {
                "id": "node-1",
                "type": "wm-pattern-filter",
                "position": {"x": 0, "y": 0},
                "data": {
                    "config": {
                        "patterns": ["Elon Musk", "Mars"],
                        "fallback_text": "Elon Musk said we will be on Mars in 2030"
                    }
                }
            },
            {
                "id": "node-2",
                "type": "wm-context-builder",
                "position": {"x": 200, "y": 0},
                "data": {}
            },
            {
                "id": "node-3",
                "type": "wm-entity-extractor",
                "position": {"x": 400, "y": 0},
                "data": {}
            },
            {
                "id": "node-4",
                "type": "wm-entity-resolver",
                "position": {"x": 600, "y": 0},
                "data": {}
            },
            {
                "id": "node-5",
                "type": "wm-memory-writer",
                "position": {"x": 800, "y": 0},
                "data": {}
            }
        ],
        "edges": [
            {"id": "e1", "source": "node-1", "target": "node-2"},
            {"id": "e2", "source": "node-2", "target": "node-3"},
            {"id": "e3", "source": "node-3", "target": "node-4"},
            {"id": "e4", "source": "node-4", "target": "node-5"}
        ]
    }

def run_test():
    print("0. Refreshing Registry...")
    try:
        res = requests.get(f"{BASE_URL}/api/nodes")
        nodes = res.json().get("nodes", [])
        print(f"   Loaded {len(nodes)} nodes.")
        print(f"   Node IDs: {[n['id'] for n in nodes]}")
    except Exception as e:
        print(f"   Failed to refresh registry: {e}")

    print("1. Creating Workflow Payload...")
    workflow = create_workflow()
    
    # Inject Input into Node 1 (Simulating Trigger or Manual Input)
    # The engine resolves inputs from upstream. For the first node, 
    # we usually need a Trigger node. 
    # But for this test, let's assume the engine can accept initial inputs 
    # or we wrap Node 1 with a Manual Trigger.
    
    # Actually, the current engine implementation in `_execute_node` resolves inputs from edges.
    # If Node 1 has no incoming edges, it gets empty inputs.
    # BUT, `PatternFilterNode` expects `text` in input.
    
    # To make this work without a Trigger node in the graph, 
    # we might need to hack the engine or add a Manual Trigger node.
    # Let's add a Manual Trigger node.
    
    # workflow["nodes"].insert(0, {
    #     "id": "trigger",
    #     "type": "trigger-manual",
    #     "position": {"x": -200, "y": 0},
    #     "data": {} 
    # })
    # workflow["edges"].insert(0, {"id": "e0", "source": "trigger", "target": "node-1"})
    
    # We need to somehow pass the input text to the trigger or the first node.
    # The `execute_workflow` endpoint doesn't seem to take inputs in the current `main.py`.
    # It just takes the workflow definition.
    
    # Let's check `trigger-manual` implementation. 
    # It likely returns whatever config/input it has?
    # Or maybe we can just start the test by manually injecting input into the context?
    # No, we can't access context from outside.
    
    # Workaround: Configure PatternFilterNode to have a default text if missing? 
    # No, that defeats the purpose.
    
    # Let's modify the test to use a "Mock Input Node" if possible, 
    # or just assume the backend is running and we can hit it.
    
    # Wait, `trigger-manual` usually accepts input from the UI when clicked.
    # But here we are calling `execute_workflow`.
    
    # Let's try to send the request and see what happens. 
    # Maybe we can modify `trigger-manual` to output static text for testing?
    # Or just assume `PatternFilterNode` will fail gracefully?
    
    # Let's add a config to `trigger-manual` to output specific text?
    # The registry says `trigger-manual` has empty config schema.
    
    # Let's try to pass input via `execute_workflow`?
    # `main.py`: `async def execute_workflow(workflow: dict)`
    # It doesn't take inputs.
    
    # OK, I will modify `trigger-manual` in the registry or just use a hardcoded input in `PatternFilterNode` for this test?
    # No, I want to test data flow.
    
    # I'll create a "Test Input" node in the registry just for this verification?
    # Or better: I'll modify `PatternFilterNode` to accept `text` from config as a fallback.
    
    print("2. Sending Execution Request...")
    try:
        res = requests.post(f"{BASE_URL}/api/workflows/execute", json=workflow)
        res.raise_for_status()
        data = res.json()
        execution_id = data["execution_id"]
        print(f"   Execution ID: {execution_id}")
    except Exception as e:
        print(f"   Failed to start execution: {e}")
        return

    print("3. Polling Status...")
    for _ in range(10):
        time.sleep(1)
        res = requests.get(f"{BASE_URL}/api/execution/{execution_id}/status")
        status = res.json()
        state = status["state"]
        print(f"   State: {state}")
        
        if state == "completed":
            print("4. Execution Completed!")
            print(json.dumps(status["outputs"], indent=2))
            break
        if state == "failed":
            print("   Execution Failed!")
            print(f"   Error: {status.get('error')}")
            break
            
if __name__ == "__main__":
    run_test()

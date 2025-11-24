import requests
import json
import time

def test_pattern_filter():
    # Load workflow
    with open("workflows/memory-waterfall.json", "r") as f:
        workflow = json.load(f)

    # Test input with multiple interesting categories
    test_text = """
    I had a meeting with John from OpenBook today. We discussed the new healthcare price transparency 
    feature for the employer dashboard. He's moving to San Francisco next month to work on the patent 
    application. I need to review the business strategy document by Friday and send feedback.
    
    Also, I've been feeling stressed about the project timeline. The doctor said my blood pressure 
    is 140/90, which is concerning. I'm thinking about investing $5000 in the company's Series A round.
    
    Question: How can we make the data pipeline more efficient for real-time price estimation?
    """

    # Update input text and map types
    for node in workflow["nodes"]:
        if node.get("data", {}).get("type"):
            node["type"] = node["data"]["type"]
            
        if node["type"] == "input-text":
            node["data"]["text"] = test_text

    print("=" * 80)
    print("TESTING INTEREST DETECTOR")
    print("=" * 80)
    print(f"\nInput text:\n{test_text}\n")
    print("=" * 80)

    try:
        response = requests.post("http://localhost:8080/api/workflows/execute", json=workflow)
        if response.status_code == 200:
            execution_id = response.json()["execution_id"]
            print(f"\n✅ Execution started: {execution_id}\n")
            
            # Wait for completion
            time.sleep(5)
            
            # Get final status
            status_res = requests.get(f"http://localhost:8080/api/execution/{execution_id}/status")
            status = status_res.json()
            
            print(f"Status: {status['state']}\n")
            
            # Find Pattern Filter output
            if "outputs" in status:
                pattern_filter_output = None
                for node_id, output in status["outputs"].items():
                    if "interesting" in output:
                        pattern_filter_output = output
                        break
                
                if pattern_filter_output:
                    print("=" * 80)
                    print("PATTERN FILTER OUTPUT")
                    print("=" * 80)
                    print(json.dumps(pattern_filter_output, indent=2))
                    print("\n" + "=" * 80)
                    print(f"DETECTED {len(pattern_filter_output.get('interesting', []))} INTERESTING ITEMS")
                    print("=" * 80)
                    
                    for i, item in enumerate(pattern_filter_output.get("interesting", []), 1):
                        print(f"\n{i}. {item['interesting_field']} (Score: {item['interesting_score']})")
                        print(f"   Reason: {item['reason']}")
                        print(f"   Snippet: {item['text_snippet']}")
                else:
                    print("⚠️  No Pattern Filter output found")
            else:
                print("⚠️  No outputs in status")
                
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pattern_filter()

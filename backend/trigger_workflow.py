import requests
import json
import time
import sys

def trigger():
    # Load workflow
    with open("workflows/memory-waterfall.json", "r") as f:
        workflow = json.load(f)

    # Update input text and map types
    for node in workflow["nodes"]:
        # Map type from data.type if available (mimic frontend AgentGraph.jsx)
        if node.get("data", {}).get("type"):
            node["type"] = node["data"]["type"]
            
        if node["type"] == "input-text":
            node["data"]["text"] = "Elon Musk is going to Mars"

    print("Triggering workflow...")
    try:
        response = requests.post("http://localhost:8080/api/workflows/execute", json=workflow)
        if response.status_code == 200:
            execution_id = response.json()["execution_id"]
            print(f"Execution started: {execution_id}")
            
            # Poll for status
            seen_logs = 0
            while True:
                status_res = requests.get(f"http://localhost:8080/api/execution/{execution_id}/status")
                status = status_res.json()
                
                logs = status.get("logs", [])
                if len(logs) > seen_logs:
                    for log in logs[seen_logs:]:
                        print(f"LOG: {log['message']}")
                    seen_logs = len(logs)
                
                if status['state'] in ['completed', 'failed']:
                    print(f"Final Status: {status['state']}")
                    break
                time.sleep(1)
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger()

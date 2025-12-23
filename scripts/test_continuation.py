import json
import requests
import sys
import os

URL = "http://localhost:8090/chat"

def test_continuation(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Sending scenario: {file_path}")
    resp = requests.post(URL, json=data)
    
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}")
        print(resp.text)
        return

    res_json = resp.json()
    analysis = res_json.get("analysis", {})
    continuation = analysis.get("continuation_assessment", {})
    
    print("\n=== Continuation Assessment (from root analysis) ===")
    print(json.dumps(continuation, ensure_ascii=False, indent=2))
    
    print("\n=== Strategy Planner Output (partial) ===")
    strategy = analysis.get("strategy", {})
    print(json.dumps(strategy.get("continuation_assessment"), ensure_ascii=False, indent=2))
    
    print("\n=== Reply Candidates ===")
    replies = res_json.get("replies", [])
    for r in replies:
        print(f"[{r.get('style')}] {r.get('text')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_continuation(sys.argv[1])
    else:
        test_continuation("data/examples/tired_night.json")

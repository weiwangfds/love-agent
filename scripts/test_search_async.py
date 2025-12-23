
import requests
import json
import time

def test_search_intent():
    url = "http://localhost:8090/chat"
    headers = {"Content-Type": "application/json"}
    
    messages = [
        {"speaker": "target", "content": "你知道泰酷辣是什么梗吗？"}
    ]
    
    payload = {
        "session_id": f"test_search_{int(time.time())}",
        "messages": messages,
        "relationship_stage": "暧昧期",
        "intimacy_level": 5
    }
    
    print("Sending request to check search intent...")
    start = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end = time.time()
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response received in {end - start:.2f}s")
        analysis = data.get("analysis", {})
        search_intent = analysis.get("search_intent", {})
        print(f"Search Intent: {search_intent}")
        kb_context = analysis.get("kb_context", {})
        print(f"KB Context (Online Search): {kb_context.get('need_online_search')}")
        print(f"Search Query: {kb_context.get('search_query')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_search_intent()

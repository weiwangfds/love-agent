import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, message, expected_search: bool):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    payload = {
        "session_id": f"test_context_meme_{int(time.time())}",
        "messages": [{"speaker": "user", "content": message}]
    }
    try:
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            res_json = response.json()
            search_intent = res_json.get("analysis", {}).get("search_intent", {})
            need_search = search_intent.get('need_search')
            
            print(f"Message: {message}")
            print(f"Need Search: {need_search}")
            
            if need_search == expected_search:
                print("✅ PASSED: Intent matched expectation")
            else:
                print(f"⚠️ FAILED: Expected {expected_search}, got {need_search}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    # Case 1: Explicit question about a meme -> Should Search
    run_test("Meme Definition", "你知道什么是city walk吗？", True)
    
    # Case 2: Using a meme as an adjective/exclamation -> Should NOT Search
    run_test("Meme Usage", "今天天气真是绝绝子", False)
    
    # Case 3: Obscure meme needing context -> Should Search
    run_test("Obscure Meme", "这简直是哈基米", True) 

if __name__ == "__main__":
    main()

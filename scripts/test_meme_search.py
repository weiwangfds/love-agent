import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, message):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    payload = {
        "session_id": f"test_meme_{int(time.time())}",
        "messages": [{"speaker": "user", "content": message}]
    }
    try:
        start_time = time.time()
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            search_intent = res_json.get("analysis", {}).get("search_intent", {})
            
            print(f"🔍 Search Intent: {search_intent.get('need_search')}")
            print(f"🔍 Search Query: {search_intent.get('search_keywords')}")
            
            if search_intent.get('need_search'):
                print("✅ PASSED: Meme triggered search")
            else:
                print("⚠️ FAILED: Meme did not trigger search")
                
            if "replies" in res_json and len(res_json["replies"]) > 0:
                print("✅ Replies generated:")
                for r in res_json["replies"]:
                    print(f"  - {r.get('text', '')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    # Test 1: Recent Internet Meme
    run_test("Meme Search 1", "什么是科目三？")
    
    # Test 2: Another Meme
    run_test("Meme Search 2", "这简直是泰酷辣")

if __name__ == "__main__":
    main()

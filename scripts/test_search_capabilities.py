import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, payload, expected_online_search):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    try:
        start_time = time.time()
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            # print("Response full dump:", json.dumps(res_json, ensure_ascii=False, indent=2))
            
            kb_ctx = res_json.get("analysis", {}).get("kb_context", {})
            search_intent = res_json.get("analysis", {}).get("search_intent", {})
            need_online = kb_ctx.get("need_online_search", False)
            
            print(f"🔍 Search Intent (RAW): {search_intent}")
            print(f"🔍 Search Intent: {search_intent.get('need_search', False)}")
            print(f"🔍 Need Online Search: {need_online}")
            print(f"🔍 Search Query: {kb_ctx.get('search_query', 'N/A')}")
            
            if "replies" in res_json and len(res_json["replies"]) > 0:
                print("✅ Replies generated:")
                for r in res_json["replies"]:
                    print(f"  - {r.get('text', '')}")
            else:
                print("⚠️ No replies found")
                
            # Verification
            if need_online == expected_online_search:
                print(f"✅ PASSED: Online search status matched expectation ({expected_online_search})")
            else:
                print(f"❌ FAILED: Expected online search {expected_online_search}, but got {need_online}")

        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    # Test 1: Query that was previously in Local KB (Shawshank Redemption)
    # Now that local KB is removed, this SHOULD trigger online search
    test_local = {
        "session_id": "test_search_local",
        "messages": [
            {"speaker": "user", "content": "你知道肖申克的救赎讲什么的吗？"}
        ]
    }
    # Update expectation: True (was False)
    run_test("1. Previous Local KB Hit (Shawshank Redemption)", test_local, expected_online_search=True)

    # Test 2: Online Search (Beijing Weather)
    # Weather is time-sensitive
    test_online = {
        "session_id": "test_search_online",
        "messages": [
            {"speaker": "target", "content": "明天我们去爬山好不好？"},
            {"speaker": "user", "content": "明天北京天气怎么样？"}
        ]
    }
    run_test("2. Online Search (Beijing Weather)", test_online, expected_online_search=True)

if __name__ == "__main__":
    time.sleep(2) # Warmup
    main()

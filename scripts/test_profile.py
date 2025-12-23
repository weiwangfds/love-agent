import requests
import json
import time

URL_PROFILE = "http://localhost:8090/profile"
URL_CHAT = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_chat(payload):
    try:
        requests.post(URL_CHAT, headers=HEADERS, data=json.dumps(payload))
    except Exception as e:
        print(f"Chat Error: {e}")

def run_test(name, session_id):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    try:
        start_time = time.time()
        # GET request for profile
        response = requests.get(f"{URL_PROFILE}?session_id={session_id}", headers=HEADERS)
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            print("Response:")
            print(json.dumps(res_json, ensure_ascii=False, indent=2))
            
            summary = res_json.get("summary")
            if summary:
                print("✅ Profile summary generated successfully")
                print(f"--- Summary Content ---\n{summary}\n-----------------------")
            else:
                print("⚠️ No summary found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    session_id = f"test_profile_{int(time.time())}"
    
    # Step 1: Seed some facts
    print("Seeding facts...")
    facts_to_seed = [
        "我超级喜欢吃抹茶味的冰淇淋。",
        "周末通常会去书店发呆一下午。",
        "最近工作压力有点大，老是失眠。",
        "养了一只叫‘皮皮’的柯基，它特别调皮。"
    ]
    for fact in facts_to_seed:
        run_chat({
            "session_id": session_id,
            "messages": [{"speaker": "user", "content": fact}]
        })
        time.sleep(0.5) # Prevent rate limit/race condition
    
    time.sleep(1)
    
    # Step 2: Get Profile Summary
    run_test("User Profile Summary", session_id)

if __name__ == "__main__":
    main()

import requests
import json
import time

URL_INITIATIVE = "http://localhost:8090/initiative"
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
        # GET request for initiative
        response = requests.get(f"{URL_INITIATIVE}?session_id={session_id}", headers=HEADERS)
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            print("Response:")
            print(json.dumps(res_json, ensure_ascii=False, indent=2))
            
            candidates = res_json.get("options", [])
            if candidates:
                print("✅ Initiative candidates generated successfully")
            else:
                print("⚠️ No candidates found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    session_id = f"test_initiative_{int(time.time())}"
    
    # Step 1: Seed some history and facts
    print("Seeding conversation history...")
    run_chat({
        "session_id": session_id,
        "messages": [{"speaker": "user", "content": "我每天晚上都习惯喝一杯热牛奶。"}]
    })
    time.sleep(1)
    
    # Step 2: Trigger Initiative
    # Expectation: Agent should use the fact (hot milk) or current time/state to generate a greeting
    run_test("Proactive Initiative", session_id)

if __name__ == "__main__":
    main()

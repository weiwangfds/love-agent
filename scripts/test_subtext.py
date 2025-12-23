import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, message):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    payload = {
        "session_id": f"test_subtext_{int(time.time())}",
        "messages": [{"speaker": "target", "content": message}],
        "relationship_stage": "暧昧期",
        "intimacy_level": 6
    }
    try:
        start_time = time.time()
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            subtext = res_json.get("analysis", {}).get("subtext", {})
            
            print(f"Target Message: {message}")
            print("--- Subtext Analysis ---")
            print(f"🕵️ Subtext: {subtext.get('subtext')}")
            print(f"💡 Action: {subtext.get('action_suggestion')}")
            print(f"📊 Confidence: {subtext.get('confidence')}")
            print("------------------------")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    # Case 1: "I'm going to shower" (Classic ambiguous)
    run_test("Subtext 1: Shower", "那我先去洗澡了")
    
    # Case 2: "Weather is nice" (Possible invitation)
    run_test("Subtext 2: Weather", "这周末天气好像不错诶")
    
    # Case 3: "Are you busy?" (Testing interest)
    run_test("Subtext 3: Busy?", "最近是不是很忙呀")

if __name__ == "__main__":
    main()

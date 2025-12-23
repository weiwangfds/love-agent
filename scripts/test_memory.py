import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, payload, step_desc):
    print(f"\n{'='*20} Running Test: {name} - {step_desc} {'='*20}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    try:
        start_time = time.time()
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            facts = res_json.get("analysis", {}).get("facts", [])
            print(f"🔍 Relevant Facts Used: {facts}")
            
            if "replies" in res_json and len(res_json["replies"]) > 0:
                print("✅ Replies generated:")
                for r in res_json["replies"]:
                    print(f"  - {r.get('text', '')}")
            else:
                print("⚠️ No replies found")
                
            return res_json
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    session_id = f"test_memory_{int(time.time())}"
    
    # Step 1: Tell the agent a fact (e.g., "I love spicy food")
    # Expectation: Agent should extract and store this fact.
    payload_1 = {
        "session_id": session_id,
        "messages": [
            {"speaker": "user", "content": "今晚去吃火锅吧，我超级爱吃辣的！"}
        ]
    }
    run_test("Memory Test", payload_1, "Step 1: Ingest Fact (Love Spicy)")
    
    time.sleep(2) # Wait for processing
    
    # Step 2: Recall the fact in a new context
    # Expectation: Agent should retrieve "User loves spicy food" and use it in the reply.
    payload_2 = {
        "session_id": session_id,
        "messages": [
            {"speaker": "user", "content": "周末我们去吃湘菜怎么样？"}
        ]
    }
    # We expect the agent to mention something about spicy food or remember the preference
    run_test("Memory Test", payload_2, "Step 2: Recall Fact (Context: Hunan Cuisine)")

if __name__ == "__main__":
    main()

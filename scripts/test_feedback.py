import requests
import json
import time

URL_FEEDBACK = "http://localhost:8090/feedback"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, payload):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    try:
        start_time = time.time()
        response = requests.post(URL_FEEDBACK, headers=HEADERS, data=json.dumps(payload))
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {duration:.2f}s")
        
        if response.status_code == 200:
            res_json = response.json()
            print("Response:")
            print(json.dumps(res_json, ensure_ascii=False, indent=2))
            
            if res_json.get("new_reply"):
                print(f"✅ Correction successful!\nNew Reply: {res_json['new_reply']}")
            else:
                print("⚠️ No new reply generated (expected for 'like' or failure)")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    session_id = f"test_feedback_{int(time.time())}"
    
    # Scenario: Agent made a greasy joke
    original_reply = "丫头，你的眼神已经出卖了你，承认吧，你就是离不开我这该死的魅力。"
    
    # Test: User dislikes it (Too greasy)
    payload = {
        "session_id": session_id,
        "original_reply": original_reply,
        "feedback_type": "dislike",
        "reason": "太油腻了，我不喜欢这种风格"
    }
    
    run_test("Negative Feedback Loop", payload)

if __name__ == "__main__":
    main()

import requests
import json
import time

URL_CHAT = "http://localhost:8090/chat"
URL_FEEDBACK = "http://localhost:8090/feedback"
HEADERS = {'Content-Type': 'application/json'}

def run_feedback(session_id):
    print("\n--- Submitting Negative Feedback ---")
    payload = {
        "session_id": session_id,
        "original_reply": "丫头，你的眼神已经出卖了你，承认吧，你就是离不开我这该死的魅力。",
        "feedback_type": "dislike",
        "reason": "太油腻了，我不喜欢这种风格，请正常点"
    }
    try:
        requests.post(URL_FEEDBACK, headers=HEADERS, data=json.dumps(payload))
        print("✅ Feedback submitted (Lesson learned)")
    except Exception as e:
        print(f"❌ Feedback Error: {e}")

def run_chat(name, session_id, message):
    print(f"\n{'='*20} Running Test: {name} {'='*20}")
    payload = {
        "session_id": session_id,
        "messages": [{"speaker": "user", "content": message}]
    }
    try:
        response = requests.post(URL_CHAT, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            res_json = response.json()
            facts = res_json.get("analysis", {}).get("facts", [])
            print(f"🔍 Facts/Lessons Retrieved: {facts}")
            
            if "replies" in res_json and len(res_json["replies"]) > 0:
                print("✅ Replies generated:")
                for r in res_json["replies"]:
                    print(f"  - {r.get('text', '')}")
            else:
                print("⚠️ No replies found")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    session_id = f"test_lesson_{int(time.time())}"
    
    # Step 1: Submit a negative feedback lesson
    run_feedback(session_id)
    
    time.sleep(2) # Allow vector store to index
    
    # Step 2: Chat again, expecting the agent to avoid being greasy
    # The agent should retrieve the lesson "User dislikes greasy style"
    run_chat("Lesson Persistence Test", session_id, "今天工作好累啊，求安慰")

if __name__ == "__main__":
    main()

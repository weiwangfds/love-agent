
import requests
import json
import time

def test_action_guide():
    url = "http://localhost:8090/chat"
    headers = {"Content-Type": "application/json"}
    
    # 场景：高暧昧，可能触发“邀约”或“表白”行动建议
    messages_flirty = [
        {"speaker": "user", "content": "其实我每次看到你，心情都会变好。"},
        {"speaker": "target", "content": "真的吗？我也是呢..."},
        {"speaker": "user", "content": "这周末那个画展，好像很适合两个人慢慢逛。"},
        {"speaker": "target", "content": "我也在关注那个画展！正想找人一起去呢。"},
        {"speaker": "user", "content": "那...要不要一起？"} # 临门一脚
    ]
    
    print("\n==================== Testing Action Guide (Critical Moment) ====================")
    payload = {
        "session_id": f"test_guide_{int(time.time())}",
        "messages": messages_flirty,
        "relationship_stage": "暧昧期",
        "intimacy_level": 7
    }
    
    try:
        start = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        end = time.time()
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get("analysis", {})
            action_guide = analysis.get("action_guide", {})
            
            print(f"Time: {end - start:.2f}s")
            if action_guide:
                print("Action Guide Triggered!")
                print(json.dumps(action_guide, indent=2, ensure_ascii=False))
            else:
                print("No Action Guide triggered (maybe not critical enough).")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_action_guide()

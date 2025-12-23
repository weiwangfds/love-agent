import requests
import json
import time

URL = "http://localhost:8090/chat"
HEADERS = {'Content-Type': 'application/json'}

def run_test(name, payload):
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
            print("Response:")
            print(json.dumps(res_json, ensure_ascii=False, indent=2))
            
            if "replies" in res_json and len(res_json["replies"]) > 0:
                print("✅ Replies generated successfully")
            else:
                print("⚠️ No replies found")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    session_id = f"test_vl_{int(time.time())}"
    
    # Test Case: Sending an image of a dog and a girl
    # Expectation: Agent should recognize the content and give a warm response
    payload = {
        "session_id": session_id,
        "messages": [
            {
                "speaker": "target",
                "type": "image",
                "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg",
                "content": "看看我拍的"
            }
        ]
    }
    run_test("Multimodal Test (Qwen-VL)", payload)

if __name__ == "__main__":
    main()

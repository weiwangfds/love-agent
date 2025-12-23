import sys
import os
import time
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import app

client = TestClient(app)

def test_ingest_flow():
    session_id = f"test_ingest_{int(time.time())}"
    
    # 1. Prepare historical messages (unordered)
    messages = [
        {
            "speaker": "user",
            "content": "Message 1 (Oldest)",
            "timestamp": 1000
        },
        {
            "speaker": "target",
            "content": "Message 3 (Newest)",
            "timestamp": 3000
        },
        {
            "speaker": "user",
            "content": "Message 2 (Middle)",
            "timestamp": 2000
        }
    ]
    
    print(f"--- Step 1: Uploading {len(messages)} messages ---")
    response = client.post("/upload_history", json={
        "session_id": session_id,
        "messages": messages
    })
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return
        
    data = response.json()
    print("Response:", data)
    assert data["status"] == "success"
    assert data["new_messages_count"] == 3
    
    # 2. Verify Order in History
    print("\n--- Step 2: Verifying History Order ---")
    hist_resp = client.get(f"/history?session_id={session_id}")
    history = hist_resp.json().get("history", [])
    
    print(f"History length: {len(history)}")
    for i, msg in enumerate(history):
        print(f"[{i}] {msg['timestamp']}: {msg['content']}")
        
    assert len(history) == 3
    assert history[0]["content"] == "Message 1 (Oldest)"
    assert history[1]["content"] == "Message 2 (Middle)"
    assert history[2]["content"] == "Message 3 (Newest)"
    
    # 3. Test Deduplication
    print("\n--- Step 3: Test Deduplication ---")
    # Upload same messages + 1 new one
    new_batch = messages + [{
        "speaker": "target", 
        "content": "Message 4 (Brand New)", 
        "timestamp": 4000
    }]
    
    response = client.post("/upload_history", json={
        "session_id": session_id,
        "messages": new_batch
    })
    
    data = response.json()
    print("Response:", data)
    assert data["new_messages_count"] == 1
    
    hist_resp = client.get(f"/history?session_id={session_id}")
    history = hist_resp.json().get("history", [])
    assert len(history) == 4
    assert history[-1]["content"] == "Message 4 (Brand New)"
    
    print("\n✅ All Ingest Tests Passed!")

if __name__ == "__main__":
    test_ingest_flow()

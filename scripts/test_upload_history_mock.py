import os
import sys
import shutil
import asyncio
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.love_agent import LoveAgent

# Mock QwenClient
class MockQwenClient:
    def __init__(self):
        pass
    
    def chat_json(self, model, messages, **kwargs):
        # Return dummy analysis
        return {
            "emotion": "neutral",
            "topics": ["test"],
            "persona": {"user": {"trait": "test"}},
            "radar": {"intimacy": 5},
            "relationship_stage": "test_stage"
        }
    
    def chat_vl(self, model, messages, **kwargs):
        return "image description"

async def test_upload_history():
    print("Starting Upload History Test...")
    
    # Setup temp dirs
    test_dir = "data/test_upload"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    config = {
        "chroma": {"persist_directory": os.path.join(test_dir, "chroma")},
        "state": {"persist_directory": os.path.join(test_dir, "state")},
        "model": {"default": "qwen-plus"}
    }
    
    # Patch QwenClient in love_agent module
    with patch('src.love_agent.QwenClient', side_effect=MockQwenClient):
        agent = LoveAgent(config)
        
        # Test Data
        session_id = "test_session_1"
        messages_1 = [
            {"speaker": "user", "content": "Hello", "timestamp": 1000},
            {"speaker": "target", "content": "Hi there", "timestamp": 1001}
        ]
        
        print("Uploading batch 1...")
        res1 = await agent.process_uploaded_history(session_id, messages_1)
        print(f"Result 1: {res1}")
        
        # Verify State
        state = agent._state_manager.get_state(session_id)
        history = state.get("history", [])
        assert len(history) == 2
        assert history[0]["content"] == "Hello"
        
        # Verify Vector Store
        # We can't easily check VS count directly without private access, but we can search
        docs = agent._history_vs.similarity_search("Hello", n_results=10)
        # Note: Chroma might take a moment or might not be consistent in memory immediately? 
        # But let's check.
        print(f"VS Search Result: {len(docs)} docs found.")
        
        # Upload Batch 2 (Overlap + New)
        messages_2 = [
            {"speaker": "target", "content": "Hi there", "timestamp": 1001}, # Duplicate
            {"speaker": "user", "content": "How are you?", "timestamp": 1002} # New
        ]
        
        print("Uploading batch 2...")
        res2 = await agent.process_uploaded_history(session_id, messages_2)
        print(f"Result 2: {res2}")
        
        # Verify State again
        state = agent._state_manager.get_state(session_id)
        history = state.get("history", [])
        assert len(history) == 3
        assert history[2]["content"] == "How are you?"
        
        print("Test Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(test_upload_history())

from typing import Dict, Any, List
import hashlib
import time
from src.vectorstore.chroma_store import ChromaStore

class HistoryIngestor:
    """
    历史记录摄入模块
    
    负责将聊天记录存入向量数据库，以便后续检索。
    使用 MD5 生成唯一消息 ID，确保去重。
    """
    def __init__(self, vector_store: ChromaStore):
        self._vs = vector_store

    def ingest(self, context: Dict[str, Any]):
        """
        摄入聊天消息到向量库
        
        Args:
            context: 上下文字典，包含 session_id 和 messages
        """
        session_id = context.get("session_id", "default")
        messages = context.get("messages", [])
        
        # Also handle new_message if present
        new_msg = context.get("new_message")
        if new_msg:
            # Avoid modifying the original list if possible, or it's fine
            # But messages might be a reference to a list used elsewhere
            # Here we just want to iterate
            if new_msg not in messages:
                messages = messages + [new_msg]

        for msg in messages:
            content = msg.get("content", "")
            if not content:
                continue
                
            speaker = msg.get("speaker", "unknown")
            timestamp = msg.get("timestamp") or int(time.time())
            
            # Create a unique ID
            # Use content and timestamp to ensure uniqueness but allow dedup
            # We assume if content, speaker and timestamp are same, it is the same message
            raw_id = f"{session_id}_{timestamp}_{content}_{speaker}"
            msg_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()
            
            metadata = {
                "session_id": session_id,
                "speaker": speaker,
                "timestamp": timestamp,
                "type": "chat_history"
            }
            
            self._vs.add_text_if_not_exists(msg_id, content, metadata)

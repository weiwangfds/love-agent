from typing import Dict, Any, List, Optional
import json
import os
import time

class StateManager:
    """
    状态管理模块
    
    负责管理和持久化用户的聊天状态，包括：
    1. 关系阶段
    2. 亲密度等级
    3. 聊天历史 (History)
    4. 关系雷达 (Radar)
    5. 人物画像 (Persona)
    6. 用户事实 (User Facts)
    
    数据存储在本地 JSON 文件中。
    """
    def __init__(self, persist_dir: str):
        self._persist_dir = persist_dir
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
            
    def _get_path(self, session_id: str) -> str:
        return os.path.join(self._persist_dir, f"state_{session_id}.json")

    def get_state(self, session_id: str) -> Dict[str, Any]:
        """
        获取指定会话的状态
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Dict: 状态字典
        """
        path = self._get_path(session_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load state from {path}: {e}. Returning default state.")
                
        # 默认状态
        return {
            "relationship_stage": "陌生/破冰",
            "intimacy_level": 1,
            "last_updated": time.time(),
            "history": [], # List of {speaker: ..., content: ..., timestamp: ...}
            "radar": {},   # Relationship Radar data
            "persona": {}, # User/Target persona
            "user_facts": [] # Extracted facts
        }

    def update_state(self, session_id: str, new_state: Dict[str, Any]):
        """
        更新状态
        
        Args:
            session_id: 会话 ID
            new_state: 需要更新的状态字段
        """
        state = self.get_state(session_id)
        # 简单更新，后续可考虑深度合并
        state.update(new_state)
        state["last_updated"] = time.time()
        
        path = self._get_path(session_id)
        # print(f"DEBUG: Saving state to {path}. Content keys: {state.keys()} History len: {len(state.get('history', []))}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取聊天历史
        
        Args:
            session_id: 会话 ID
            
        Returns:
            List[Dict]: 消息列表
        """
        state = self.get_state(session_id)
        hist = state.get("history", [])
        # print(f"DEBUG: get_history for {session_id} returned {len(hist)} items")
        return hist

    def append_message(self, session_id: str, message: Dict[str, Any]):
        """
        追加一条消息到历史
        
        Args:
            session_id: 会话 ID
            message: 消息字典 {speaker: 'user'/'target', content: '...', timestamp: ...}
        """
        state = self.get_state(session_id)
        if "history" not in state:
            state["history"] = []
        
        # 确保有时间戳
        if "timestamp" not in message or not message["timestamp"]:
            message["timestamp"] = int(time.time())
            
        state["history"].append(message)
        self.update_state(session_id, {"history": state["history"]})

    def update_radar(self, session_id: str, radar_data: Dict[str, Any]):
        """
        更新关系雷达数据
        
        Args:
            session_id: 会话 ID
            radar_data: 雷达数据字典
        """
        self.update_state(session_id, {"radar": radar_data})

    def update_persona(self, session_id: str, persona_data: Dict[str, Any]):
        """
        更新人物画像数据
        
        Args:
            session_id: 会话 ID
            persona_data: 画像数据字典
        """
        self.update_state(session_id, {"persona": persona_data})

    def merge_history(self, session_id: str, new_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并新的消息到现有历史 (去重并排序)
        
        Args:
            session_id: 会话 ID
            new_messages: 新的消息列表
            
        Returns:
            List[Dict]: 实际新增的消息列表
        """
        state = self.get_state(session_id)
        current_history = state.get("history", [])
        
        # 创建现有消息的签名集合，用于快速去重
        # 签名: (timestamp, speaker, content)
        existing_signatures = set()
        for msg in current_history:
            ts = msg.get("timestamp", 0)
            sp = msg.get("speaker", "")
            ct = msg.get("content", "").strip()
            existing_signatures.add((ts, sp, ct))
            
        added_messages = []
        for msg in new_messages:
            ts = msg.get("timestamp")
            if ts is None:
                # 如果缺少时间戳，使用当前时间
                ts = int(time.time())
                msg["timestamp"] = ts
            
            sp = msg.get("speaker", "")
            ct = msg.get("content", "").strip()
            
            if (ts, sp, ct) not in existing_signatures:
                current_history.append(msg)
                added_messages.append(msg)
                existing_signatures.add((ts, sp, ct))
        
        if added_messages:
            # 按时间戳排序
            current_history.sort(key=lambda x: x.get("timestamp", 0))
            self.update_state(session_id, {"history": current_history})
            
        return added_messages

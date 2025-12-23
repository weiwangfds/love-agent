from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import CHAT_REVIEW_PROMPT

class ChatReviewer:
    """
    聊天复盘专家
    
    对一段完整的聊天记录进行复盘，指出优点、缺点和改进建议。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def review(self, conversation_history: str) -> Dict[str, Any]:
        """
        复盘聊天历史
        
        Args:
            conversation_history: 聊天记录文本
            
        Returns:
            Dict: 复盘结果 (JSON)
        """
        user_prompt = CHAT_REVIEW_PROMPT.replace(
            "{conversation_history}", conversation_history
        )
        
        messages = [
            {"role": "system", "content": "你是资深情感咨询师，严格输出JSON。"},
            {"role": "user", "content": user_prompt},
        ]
        
        # 使用稍高的温度以获得更有建设性和创造性的反馈
        return self._client.chat_json(self._model, messages, temperature=0.3)

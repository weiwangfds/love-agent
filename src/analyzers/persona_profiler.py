from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import PERSONALITY_ANALYSIS_PROMPT


class PersonaProfiler:
    """
    人物画像分析器
    
    根据对话历史，分析目标对象的人物性格、MBTI、关键词等特征。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def profile(self, context_window: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        生成人物画像
        
        Args:
            context_window: 对话历史窗口
            
        Returns:
            Dict: 人物画像数据 (JSON)
        """
        history_lines = []
        for m in context_window:
            speaker = m.get("speaker") or ""
            content = m.get("content") or ""
            history_lines.append(f"{speaker}: {content}")
        conversation_history = "\n".join(history_lines)
        
        user_prompt = PERSONALITY_ANALYSIS_PROMPT.replace("{conversation_history}", conversation_history)
        messages = [
            {"role": "system", "content": "你是专业的性格分析助手，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=0.2)
        return resp

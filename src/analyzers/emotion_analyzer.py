from typing import Dict, Any, List
import re
from src.model.qwen_client import QwenClient
from src.prompts.prompts import EMOTION_DETECTION_PROMPT


class EmotionAnalyzer:
    """
    情绪分析器
    
    分析用户对话中的情绪状态，结合规则匹配（关键词）和 LLM 深度分析。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def analyze(self, context: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        执行情绪分析
        
        Args:
            context: 对话上下文窗口
            
        Returns:
            Dict: 包含情绪分类、置信度和详细分析结果
        """
        latest = context[-1]["content"] if context else ""
        
        # 简单的规则匹配作为预判
        negative_hits = len(re.findall(r"(糟|累|烦|无语|难受|不开心|生气|算了)", latest))
        emotion_guess = "negative" if negative_hits >= 1 else "neutral"
        
        # 构建历史记录字符串
        history_lines = []
        for m in context[:-1]:
            history_lines.append(f"{m.get('speaker','')}: {m.get('content','')}")
        context_history = "\n".join(history_lines)
        
        # 调用 LLM 进行深度分析
        user_prompt = (
            EMOTION_DETECTION_PROMPT.replace("{current_message}", latest).replace("{context_history}", context_history)
        )
        messages = [
            {"role": "system", "content": "你是中文对话的情绪识别专家，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=0.2)
        
        return {
            "emotion": emotion_guess,
            "confidence": 0.7 if emotion_guess == "negative" else 0.5,
            "detail": resp,
        }

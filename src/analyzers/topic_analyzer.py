from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import TOPIC_ANALYSIS_PROMPT


class TopicAnalyzer:
    """
    话题分析器
    
    识别当前对话的话题，用于辅助知识库检索和话题转移策略。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def analyze(self, latest_message: str, context_history: str) -> List[str]:
        """
        分析对话话题
        
        Args:
            latest_message: 最新一条消息
            context_history: 上下文历史
            
        Returns:
            List[str]: 话题列表
        """
        user_prompt = (
            TOPIC_ANALYSIS_PROMPT.replace("{current_message}", str(latest_message))
            .replace("{context_history}", str(context_history))
        )
        messages = [
            {"role": "system", "content": "你是对话话题分析专家，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=0.1)
        return resp.get("topics", [])

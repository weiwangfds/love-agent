from typing import Dict, Any
from src.model.qwen_client import QwenClient
from src.prompts.prompts import SAFETY_CHECK_PROMPT


class SafetyChecker:
    """
    安全检测模块
    
    负责对 Agent 生成的回复进行安全检查，确保不包含
    政治敏感、色情暴力、侮辱谩骂等不适宜内容。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def check(self, reply_content: str) -> Dict[str, Any]:
        """
        检查回复内容安全性
        
        Args:
            reply_content: 回复内容
            
        Returns:
            Dict: 包含 is_safe 字段的检查结果
        """
        user_prompt = SAFETY_CHECK_PROMPT.replace("{reply_content}", str(reply_content))
        messages = [
            {"role": "system", "content": "你是回复安全检测助手，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=0.0)
        return resp


from typing import Dict, Any
from src.model.qwen_client import QwenClient
from src.prompts.prompts import EMOTIONAL_FIRST_AID_PROMPT


class EmpathyEngine:
    """
    共情引擎
    
    当检测到对方情绪低落或负面时，生成具有安抚和共情效果的回复建议。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def generate(self, target_message: str, current_emotion: str, emotion_score: int, 
                 relationship_stage: str = "未知", persona: Dict[str, Any] = None, 
                 user_facts: list = None, temperature: float = 0.7) -> Dict[str, Any]:
        """
        生成共情回复
        
        Args:
            target_message: 对方的消息
            current_emotion: 当前情绪分类
            emotion_score: 情绪强度
            relationship_stage: 关系阶段
            persona: 对方画像
            user_facts: 用户事实
            temperature: 随机性参数
            
        Returns:
            Dict: 包含建议回复列表 (replies)
        """
        user_prompt = (
            EMOTIONAL_FIRST_AID_PROMPT.replace("{target_message}", str(target_message))
            .replace("{current_emotion}", str(current_emotion))
            .replace("{emotion_score}", str(emotion_score))
            .replace("{relationship_stage}", str(relationship_stage))
            .replace("{persona}", str(persona or {}))
            .replace("{user_facts}", str(user_facts or []))
        )
        messages = [
            {"role": "system", "content": "你是中文情感急救助手，生成口语自然的三段式回复（共情+安慰+解决建议），严格输出JSON，包含replies数组，每条含text与reason。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=temperature)
        return resp

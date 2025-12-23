from typing import Dict, Any
from src.model.qwen_client import QwenClient
from src.prompts.prompts import STRATEGY_PLANNING_PROMPT


class StrategyPlanner:
    """
    策略规划模块
    
    负责基于当前的人物画像、关系状态、情感分析等信息，
    规划下一步的聊天策略。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def plan(
        self,
        personality_profile: Dict[str, Any],
        emotion_analysis: Dict[str, Any],
        relationship_stage: str,
        intimacy_level: int,
        humor_level: int,
        current_appellation: str,
        user_gender: str = "未知",
        target_gender: str = "未知",
        conversation_history: str = "",
    ) -> Dict[str, Any]:
        """
        制定聊天策略
        
        Args:
            personality_profile: 人物画像
            emotion_analysis: 情感分析结果
            relationship_stage: 关系阶段
            intimacy_level: 亲密度等级
            humor_level: 幽默等级
            current_appellation: 当前称呼
            user_gender: 用户性别
            target_gender: 对方性别
            conversation_history: 对话历史
            
        Returns:
            Dict: 包含策略建议的 JSON
        """
        user_prompt = (
            STRATEGY_PLANNING_PROMPT.replace("{personality_profile}", str(personality_profile))
            .replace("{emotion_analysis}", str(emotion_analysis))
            .replace("{relationship_stage}", str(relationship_stage))
            .replace("{intimacy_level}", str(intimacy_level))
            .replace("{humor_level}", str(humor_level))
            .replace("{current_appellation}", str(current_appellation))
            .replace("{user_gender}", str(user_gender))
            .replace("{target_gender}", str(target_gender))
            .replace("{conversation_history}", str(conversation_history))
        )
        messages = [
            {"role": "system", "content": "你是中文恋爱策略规划助手，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=0.3)
        return resp

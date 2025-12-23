from typing import Dict, Any, List
import datetime
from src.prompts.prompts import INITIATIVE_PROMPT


class InitiativeGenerator:
    """
    主动搭讪生成器
    
    在长时间无对话或需要主动破冰时，生成开启话题的建议。
    """
    def __init__(self, client: Any, model: str):
        self._client = client
        self._model = model

    def generate(self, relationship_stage: str, intimacy_level: int, persona: Dict[str, Any], user_facts: List[str], last_chat_time: str, environment_context: str) -> Dict[str, Any]:
        """
        生成搭讪建议
        
        Args:
            relationship_stage: 关系阶段
            intimacy_level: 亲密度等级
            persona: 对方画像
            user_facts: 相关事实
            last_chat_time: 上次聊天时间
            environment_context: 环境上下文（天气、节日等）
            
        Returns:
            Dict: 建议内容
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        user_prompt = (
            INITIATIVE_PROMPT.replace("{current_time}", current_time)
            .replace("{last_chat_time}", str(last_chat_time))
            .replace("{environment_context}", str(environment_context))
            .replace("{relationship_stage}", str(relationship_stage))
            .replace("{intimacy_level}", str(intimacy_level))
            .replace("{persona}", str(persona))
            .replace("{user_facts}", str(user_facts))
        )
        
        messages = [
            {"role": "system", "content": "你是高情商恋爱军师，善于制造自然、有趣的话题开场。严格输出JSON，包含options数组。"},
            {"role": "user", "content": user_prompt},
        ]
        
        return self._client.chat_json(self._model, messages, temperature=0.9)

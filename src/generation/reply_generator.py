from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import REPLY_COMPOSITION_PROMPT


class ReplyGenerator:
    """
    回复生成器
    
    综合各种上下文信息（策略、画像、记忆、检索结果等），生成最终的回复候选项。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def generate(
        self,
        target_message: str,
        relationship_stage: str,
        intimacy_level: int,
        humor_level: int,
        reply_strategy: str,
        language_style: str,
        current_appellation: str,
        kb_context: Dict[str, Any],
        retrieval_context: List[Dict[str, Any]] | None = None,
        user_gender: str = "未知",
        target_gender: str = "未知",
        topic_management: Dict[str, Any] | None = None,
        boundary_assessment: Dict[str, Any] | None = None,
        action_guide: Dict[str, Any] | None = None,
        user_facts: List[str] | None = None,
        temperature: float = 0.8,
    ) -> Dict[str, Any]:
        """
        生成回复
        
        Args:
            target_message: 对方消息
            relationship_stage: 关系阶段
            intimacy_level: 亲密度
            humor_level: 幽默等级
            reply_strategy: 回复策略
            language_style: 语言风格
            current_appellation: 当前称呼
            kb_context: 知识库上下文
            retrieval_context: 历史检索上下文
            user_gender: 用户性别
            target_gender: 对方性别
            topic_management: 话题管理建议
            boundary_assessment: 边界评估
            action_guide: 关键行动指南
            user_facts: 用户事实
            temperature: 随机性
            
        Returns:
            Dict: 包含多个回复选项的 JSON
        """
        retrieval_materials = str(retrieval_context or [])
        kb_materials = str(kb_context or {})
        topic_management_str = str(topic_management or {})
        boundary_assessment_str = str(boundary_assessment or {})
        action_guide_str = str(action_guide or {})
        facts_str = str(user_facts or [])
        
        # 检查是否需要在线搜索
        enable_search = kb_context.get("need_online_search", False)
        
        user_prompt = (
            REPLY_COMPOSITION_PROMPT.replace("{target_message}", str(target_message))
            .replace("{relationship_stage}", str(relationship_stage))
            .replace("{intimacy_level}", str(intimacy_level))
            .replace("{humor_level}", str(humor_level))
            .replace("{reply_strategy}", str(reply_strategy))
            .replace("{language_style}", str(language_style))
            .replace("{current_appellation}", str(current_appellation))
            .replace("{retrieval_materials}", retrieval_materials)
            .replace("{kb_materials}", kb_materials)
            .replace("{user_gender}", str(user_gender))
            .replace("{target_gender}", str(target_gender))
            .replace("{topic_management}", topic_management_str)
            .replace("{boundary_assessment}", boundary_assessment_str)
            .replace("{action_guide}", action_guide_str)
            .replace("{user_facts}", facts_str)
        )
        messages = [
            {"role": "system", "content": "你是中文恋爱聊天助手，生成口语自然的微信聊天候选，严格输出JSON，仅包含replies数组。"},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._client.chat_json(self._model, messages, temperature=temperature, enable_search=enable_search)
        return resp

from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import RELATIONSHIP_ANALYSIS_PROMPT


class RelationshipAnalyzer:
    """
    关系状态分析器
    
    分析当前两人关系的阶段、亲密度、信任度等维度。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def analyze(self, conversation_history: str) -> Dict[str, Any]:
        """
        分析关系状态
        
        Args:
            conversation_history: 对话历史文本
            
        Returns:
            Dict: 关系分析结果 (JSON)
        """
        user_prompt = RELATIONSHIP_ANALYSIS_PROMPT.replace(
            "{conversation_history}", conversation_history
        )
        messages = [
            {"role": "system", "content": "你是恋爱关系分析专家，严格输出JSON。"},
            {"role": "user", "content": user_prompt},
        ]
        return self._client.chat_json(self._model, messages, temperature=0.5)

    def update_state(self, conversation_history: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于新的历史和当前状态更新关系状态
        
        Args:
            conversation_history: 对话历史
            current_state: 当前存储的状态
            
        Returns:
            Dict: 更新后的状态
        """
        # 目前简化为重新分析，后续可加入状态平滑过渡逻辑
        return self.analyze(conversation_history)

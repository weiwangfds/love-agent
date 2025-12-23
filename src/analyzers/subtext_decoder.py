from typing import Dict, Any
from src.model.qwen_client import QwenClient
from src.prompts.prompts import SUBTEXT_DECODING_PROMPT


class SubtextDecoder:
    """
    潜台词解码器
    
    深度分析对方话语背后的真实意图和隐含情绪。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def decode(
        self,
        target_message: str,
        context_history: str,
        relationship_stage: str,
    ) -> Dict[str, Any]:
        """
        解码潜台词
        
        Args:
            target_message: 目标消息
            context_history: 上下文
            relationship_stage: 关系阶段
            
        Returns:
            Dict: 解码结果 (JSON)
        """
        # 如果目标消息为空，直接返回空结果
        if not target_message:
            return {}
            
        user_prompt = (
            SUBTEXT_DECODING_PROMPT.replace("{target_message}", str(target_message))
            .replace("{context_history}", str(context_history))
            .replace("{relationship_stage}", str(relationship_stage))
        )
        
        messages = [
            {"role": "system", "content": "你是恋爱读心神探，敏锐洞察潜台词，严格输出JSON。"},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            resp = self._client.chat_json(self._model, messages, temperature=0.5)
            # print(f"DEBUG SUBTEXT RESP: {resp}") # Uncomment for debugging
            return resp
        except Exception as e:
            print(f"潜台词解码错误: {e}")
            return {}

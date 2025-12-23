from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.prompts.prompts import RESEARCH_INTENT_PROMPT


class SearchIntentAnalyzer:
    """
    搜索意图分析器
    
    判断用户当前的问题是否需要借助外部知识库或联网搜索来回答。
    """
    def __init__(self, client: QwenClient, model: str):
        self._client = client
        self._model = model

    def analyze(self, latest_message: str, context_history: str) -> Dict[str, Any]:
        """
        分析搜索意图
        
        Args:
            latest_message: 最新消息
            context_history: 上下文历史
            
        Returns:
            Dict: 包含 need_search (bool) 和 search_query (str)
        """
        user_prompt = (
            RESEARCH_INTENT_PROMPT.replace("{current_message}", str(latest_message))
            .replace("{context_history}", str(context_history))
        )
        # print(f"DEBUG SEARCH PROMPT:\n{user_prompt}")
        messages = [
            {"role": "system", "content": "你是对话分析专家，严格输出JSON对象。"},
            {"role": "user", "content": user_prompt},
        ]
        # 使用极低温度以保证逻辑判断的确定性
        resp = self._client.chat_json(self._model, messages, temperature=0.01) 
        
        # 调试日志
        with open("debug_search_intent.log", "a") as f:
            f.write(f"\n--- New Analysis ---\nInput: {latest_message}\nPrompt: {user_prompt}\nResponse: {resp}\n")
            
        # 强制布尔值转换
        if isinstance(resp.get("need_search"), str):
            resp["need_search"] = str(resp["need_search"]).lower() == "true"
        return resp

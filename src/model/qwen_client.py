from typing import Any, Dict, List
import os
import json
from openai import OpenAI


class QwenClient:
    """
    Qwen API 客户端封装
    
    负责与通义千问 (Qwen) 模型 API 进行交互，提供文本和视觉对话能力。
    """
    def __init__(self):
        """
        初始化客户端
        
        从环境变量读取 API Key 和 Base URL。
        """
        api_key = os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self._client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def chat_json(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        enable_search: bool = False,
    ) -> Dict[str, Any]:
        """
        发送聊天请求并期望返回 JSON 格式数据
        
        Args:
            model: 模型名称 (e.g., "qwen-plus")
            messages: 消息列表
            temperature: 随机性参数
            enable_search: 是否启用网络搜索 (Qwen 插件能力)
            
        Returns:
            Dict: 解析后的 JSON 响应
        """
        if self._client is None:
            raise RuntimeError("DASHSCOPE_API_KEY 未设置，无法使用 LLM。")
            
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        # 仅当模型支持时才添加 response_format (qwen-turbo/plus/max 通常支持)
        # 但为了稳健性，我们主要依赖 Prompt 约束，并在此处进行解析尝试
        # kwargs["response_format"] = {"type": "json_object"} 
        
        if enable_search:
            kwargs["extra_body"] = {"enable_search": True}
            
        resp = self._client.chat.completions.create(**kwargs)
        # print(f"DEBUG LLM RAW RESP: {resp.choices[0].message.content}") 
        try:
            content = resp.choices[0].message.content
            # 处理 markdown json 代码块
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            elif content.startswith("```"):
                content = content.replace("```", "")
            return json.loads(content)
        except Exception as e:
            print(f"JSON 解析错误: {e}, 内容: {resp.choices[0].message.content}")
            # 降级策略: 尝试提取 { } 之间的内容
            try:
                content = resp.choices[0].message.content
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    json_str = content[start : end + 1]
                    return json.loads(json_str)
            except:
                pass
            return {}

    def chat_vl(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
    ) -> str:
        """
        发送视觉理解请求 (VL Model)
        
        Args:
            model: 视觉模型名称 (e.g., "qwen-vl-plus")
            messages: 包含图片和文本的消息列表
            
        Returns:
            str: 模型回复的文本内容
        """
        if self._client is None:
            raise RuntimeError("DASHSCOPE_API_KEY 未设置，无法使用 LLM。")
            
        # 确保使用的是 VL 模型
        # if not model.endswith("vl-plus") and not model.endswith("vl-max"):
        #     model = "qwen-vl-plus"
            
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        resp = self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content

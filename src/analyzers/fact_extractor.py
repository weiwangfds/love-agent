from typing import List, Any


class FactExtractor:
    """
    事实提取器
    
    从对话中提取关于用户的客观事实（如喜好、习惯、背景等）。
    """
    def __init__(self, client: Any, model: str):
        self._client = client
        self._model = model

    def extract(self, latest_text: str, history_str: str) -> List[str]:
        """
        提取事实
        
        Args:
            latest_text: 最新消息文本
            history_str: 历史记录文本
            
        Returns:
            List[str]: 提取到的事实列表
        """
        # 临时实现
        return []

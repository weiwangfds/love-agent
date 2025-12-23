from typing import List, Dict, Any
import re


class OpportunityDetector:
    """
    机会探测模块
    
    负责从对方的消息中探测潜在的邀约、升级关系的机会。
    目前基于关键词和正则匹配进行简单评分。
    """
    def score(self, latest_text: str) -> float:
        """
        对消息进行机会评分
        
        Args:
            latest_text: 最新消息文本
            
        Returns:
            float: 机会分数 (0.0 - 1.0)
        """
        signals = [
            r"(周末|晚上|有空|下次|一起|约|去看|想去)",
            r"(哈哈|嘿嘿|🙂|😊|😉)",
            r"(可以|不错|好呀|可以啊|可以的)",
        ]
        s = 0
        for pat in signals:
            if re.search(pat, latest_text):
                s += 0.25
        if re.search(r"(不太|算了|没空|改天|再说)", latest_text):
            s -= 0.2
        if s < 0:
            s = 0.0
        if s > 1:
            s = 1.0
        return round(s, 2)

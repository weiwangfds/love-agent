from typing import Dict, Any, Optional
import datetime
import requests
import json
import pytz
from lunarcalendar import Converter, Solar

class ContextAwareness:
    """
    环境感知模块
    
    负责获取和处理当前的环境信息，包括：
    1. 时间信息 (日期、时间、星期)
    2. 节日信息 (公历、农历、特殊日子)
    3. 天气信息 (基于城市)
    
    用于为回复生成提供上下文环境感。
    """
    def __init__(self, timezone: str = "Asia/Shanghai"):
        self._timezone = pytz.timezone(timezone)
        # In a real app, you might use a paid weather API key
        # Here we can use open APIs or mock for demonstration
        pass

    def get_context(self, city: str = "北京") -> Dict[str, Any]:
        """
        获取当前环境上下文
        
        Args:
            city: 城市名称
            
        Returns:
            Dict: 包含时间、节日、天气等信息的字典
        """
        now = datetime.datetime.now(self._timezone)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        weekday = weekday_map[now.weekday()]
        
        # 1. Holiday Check (Simple rule-based for demo)
        holiday = self._check_holiday(now)
        
        # 2. Weather Check (Mock or simple API)
        # For demo purposes, we'll simulate weather or use a public free API if available without key
        # wttr.in is a great free weather service for text/json
        weather_info = self._get_weather(city)
        
        context_str = f"现在是{date_str} {time_str} {weekday}"
        if holiday:
            context_str += f"，今天是{holiday}"
        if weather_info:
            context_str += f"，{city}天气：{weather_info}"
            
        return {
            "context_str": context_str,
            "holiday": holiday,
            "weather": weather_info,
            "timestamp": now.timestamp()
        }

    def _check_holiday(self, date_obj: datetime.datetime) -> Optional[str]:
        month = date_obj.month
        day = date_obj.day
        year = date_obj.year
        
        # 1. Solar Holidays
        solar_holidays = {
            (2, 14): "情人节",
            (5, 20): "520网络情人节",
            (5, 21): "521网络情人节",
            (12, 24): "平安夜",
            (12, 25): "圣诞节",
            (1, 1): "元旦",
            (10, 1): "国庆节",
            (3, 8): "妇女节",
            (11, 11): "光棍节/购物节",
        }
        
        if (month, day) in solar_holidays:
            return solar_holidays[(month, day)]
            
        # 2. Lunar Holidays (Calculated dynamically)
        try:
            solar = Solar(year, month, day)
            lunar = Converter.Solar2Lunar(solar)
            
            lunar_month = lunar.month
            lunar_day = lunar.day
            
            lunar_holidays = {
                (1, 1): "春节",
                (1, 15): "元宵节",
                (7, 7): "七夕节", # Chinese Valentine's Day
                (8, 15): "中秋节",
                (9, 9): "重阳节",
                (12, 8): "腊八节",
            }
            
            # Special handling for Lunar New Year's Eve (除夕)
            # Usually last day of 12th lunar month
            # For simplicity in this demo, we check if tomorrow is Spring Festival
            # A more robust way requires checking next day
            
            if (lunar_month, lunar_day) in lunar_holidays:
                return lunar_holidays[(lunar_month, lunar_day)]
                
        except Exception as e:
            print(f"Lunar conversion error: {e}")
            
        # 3. Check for special weekdays
        weekday = date_obj.weekday()
        if weekday == 3: # Thursday
            return "疯狂星期四 (V我50)"
        if weekday >= 5: # 5=Saturday, 6=Sunday
            return "周末"
            
        return None

    def _get_weather(self, city: str) -> str:
        try:
            # Using wttr.in which is free and doesn't require API key
            # format=%C+%t => Condition + Temperature
            resp = requests.get(f"https://wttr.in/{city}?format=%C+%t", timeout=2)
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass
        return "未知天气"

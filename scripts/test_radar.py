
import requests
import json
import time

def test_relationship_radar():
    url = "http://localhost:8090/chat"
    headers = {"Content-Type": "application/json"}
    
    # 场景1：顺风局 - 暧昧升温
    messages_good = [
        {"speaker": "user", "content": "这周末有空吗？"},
        {"speaker": "target", "content": "有啊，怎么啦？"},
        {"speaker": "user", "content": "想带你去那家新开的猫咖，感觉你会喜欢。"},
        {"speaker": "target", "content": "哇！真的吗？我最近正好想去撸猫呢！太懂我了吧~"},
        {"speaker": "user", "content": "必须的，那我周六下午去接你？"},
        {"speaker": "target", "content": "好呀，期待！穿那件你夸过的白裙子见你~"}
    ]
    
    # 场景2：逆风局 - 舔狗预警
    messages_bad = [
        {"speaker": "user", "content": "早安！今天天气不错，记得带伞哦。"},
        {"speaker": "target", "content": "嗯。"},
        {"speaker": "user", "content": "中午吃的什么呀？"},
        {"speaker": "target", "content": "饭。"},
        {"speaker": "user", "content": "晚上有空出来看电影吗？最近那个科幻片上映了。"},
        {"speaker": "target", "content": "没空，忙。"},
        {"speaker": "user", "content": "那周末呢？"},
        {"speaker": "target", "content": "再说吧，洗澡去了。"}
    ]
    
    scenarios = [
        ("Good (Flirty/Promising)", messages_good),
        ("Bad (Cold/Rejection)", messages_bad)
    ]
    
    for name, msgs in scenarios:
        print(f"\n==================== Testing Radar: {name} ====================")
        payload = {
            "session_id": f"test_radar_{int(time.time())}",
            "messages": msgs,
            # Let the agent infer stage/radar
        }
        
        try:
            start = time.time()
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            end = time.time()
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                radar = analysis.get("radar", {})
                overall = analysis.get("overall_analysis", "N/A")
                
                print(f"Time: {end - start:.2f}s")
                print(f"Overall Analysis: {overall}")
                print("Radar Chart:")
                for dim, detail in radar.items():
                    # Check if detail is dict or just score (depending on prompt adherence)
                    if isinstance(detail, dict):
                        print(f"  - {dim}: {detail.get('score')} ({detail.get('reason')})")
                    else:
                        print(f"  - {dim}: {detail}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_relationship_radar()

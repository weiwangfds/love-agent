from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import sys
import base64

# 将项目根目录添加到系统路径，以便导入 src 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.love_agent import LoveAgent, load_config

# 初始化 FastAPI 应用
app = FastAPI(
    title="Love Agent API",
    description="恋爱高情商辅助助手 API，提供聊天、分析、画像、策略等核心功能",
    version="1.0.0"
)

# 初始化 LoveAgent 实例
# 加载配置文件并实例化核心代理对象
try:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config/config.yaml")
    cfg = load_config(config_path)
    agent = LoveAgent(cfg)
except Exception as e:
    print(f"Error initializing LoveAgent: {e}")
    agent = None

# --- 数据模型定义 (Pydantic Models) ---

class Message(BaseModel):
    """
    聊天消息模型
    """
    speaker: str = Field(..., description="发言者: 'user' (我方) 或 'target' (对方)")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[int] = Field(None, description="时间戳 (Unix Timestamp)")
    type: Optional[str] = Field(None, description="消息类型: 'text' (文本), 'image' (图片) 等") # 默认为 text
    url: Optional[str] = Field(None, description="图片URL (仅当 type='image' 时有效)")

class ReviewRequest(BaseModel):
    """
    聊天复盘请求模型
    """
    messages: List[Message] = Field(..., description="要复盘的聊天记录列表")

class Highlight(BaseModel):
    """
    复盘高光时刻
    """
    content: str = Field(..., description="高光对话内容")
    reason: str = Field(..., description="判定为高光的原因")

class Lowlight(BaseModel):
    """
    复盘扣分项/待改进项
    """
    content: str = Field(..., description="待改进的对话内容")
    reason: str = Field(..., description="判定为扣分项的原因")
    suggestion: str = Field(..., description="改进建议")

class ReviewResponse(BaseModel):
    """
    复盘响应模型
    """
    highlights: List[Highlight] = Field(..., description="高光时刻列表")
    lowlights: List[Lowlight] = Field(..., description="扣分项列表")
    score: int = Field(..., description="总体评分 (0-100)")
    summary: str = Field(..., description="整体评价摘要")

class ChatRequest(BaseModel):
    """
    聊天请求模型
    """
    session_id: str = Field(..., description="会话唯一标识符")
    relationship_stage: Optional[str] = Field(None, description="关系阶段: 破冰/暧昧/热恋/冷淡/分手/复合等 (可选，若不传则自动推断或沿用历史状态)")
    intimacy_level: Optional[int] = Field(None, ge=0, le=10, description="亲密度等级 (0-10) (可选)")
    humor_level: Optional[int] = Field(None, ge=0, le=5, description="幽默程度 (0-5) (可选)")
    current_appellation: Optional[str] = Field(None, description="当前对对方的称呼 (可选)")
    user_gender: Optional[str] = Field(None, description="用户性别 (可选)")
    target_gender: Optional[str] = Field(None, description="对方性别 (可选)")
    messages: List[Message] = Field(default=[], description="完整的对话历史记录 (可选)")
    new_message: Optional[Message] = Field(None, description="最新的一条消息 (推荐使用此字段进行增量更新)")

class Reply(BaseModel):
    """
    Agent 生成的回复
    """
    text: str = Field(..., description="回复内容")
    reason: str = Field(..., description="生成该回复的设计思路/理由")

class Analysis(BaseModel):
    """
    对话分析结果
    """
    emotion: Dict[str, Any] = Field(..., description="情绪分析结果")
    topics: List[str] = Field(..., description="话题列表")
    persona: Dict[str, Any] = Field(..., description="更新后的人物画像")
    strategy: Dict[str, Any] = Field(..., description="当前策略状态")
    kb_context: Optional[Dict[str, Any]] = Field(None, description="检索到的知识库上下文")
    search_intent: Optional[Dict[str, Any]] = Field(None, description="搜索意图分析")
    facts: Optional[List[str]] = Field(None, description="提取的新事实")
    subtext: Optional[Dict[str, Any]] = Field(None, description="潜台词解读")
    radar: Optional[Dict[str, Any]] = Field(None, description="关系雷达评分")
    overall_analysis: Optional[str] = Field(None, description="整体局势分析")
    action_guide: Optional[Dict[str, Any]] = Field(None, description="关键行动指南")

class ChatResponse(BaseModel):
    """
    聊天响应模型
    """
    replies: List[Reply] = Field(..., description="建议回复列表")
    analysis: Analysis = Field(..., description="详细的分析报告")

class FeedbackRequest(BaseModel):
    """
    用户反馈请求模型
    """
    session_id: str
    original_reply: str = Field(..., description="Agent 生成的原始回复内容")
    feedback_type: str = Field(..., description="反馈类型: 'like' (点赞) 或 'dislike' (点踩)")
    reason: Optional[str] = Field(None, description="具体的反馈理由")

class HistoryUploadRequest(BaseModel):
    """
    历史记录上传请求模型
    """
    session_id: str
    messages: List[Message] = Field(..., description="要上传的消息列表")

# --- API 接口定义 ---

@app.post("/upload_history")
async def upload_history(request: HistoryUploadRequest):
    """
    上传聊天历史记录
    
    功能:
    1. 接收批量的聊天记录。
    2. 调用 Agent 进行去重、排序、存储。
    3. 触发画像更新和关系雷达分析。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        # Convert messages to dicts
        history = [m.model_dump() for m in request.messages]
        result = await agent.process_uploaded_history(request.session_id, history)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    """
    接收用户对 Agent 回复的反馈
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        # Adapt to new signature: user_feedback, last_agent_reply
        user_fb = f"{request.feedback_type}: {request.reason}" if request.reason else request.feedback_type
        result = await agent.handle_feedback(
            session_id=request.session_id,
            user_feedback=user_fb,
            last_agent_reply=request.original_reply
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review", response_model=ReviewResponse)
async def review(request: ReviewRequest):
    """
    聊天复盘接口
    
    对提供的聊天记录进行深度分析，识别高光时刻和扣分项，给出评分和改进建议。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        # Convert messages to dicts
        history = [m.model_dump() for m in request.messages]
        result = await agent.review_chat(history)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to Love Agent API. Use /chat to generate replies."}

@app.get("/profile")
async def profile(session_id: str):
    """
    获取用户画像
    
    返回基于历史对话生成的对方人物画像（性格、MBTI、关键词）及提取的事实标签。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        # Get structured profile data
        profile_data = agent.get_profile(session_id)
        # Generate summary
        summary = agent.generate_profile_summary(session_id)
        
        return {
            "summary": summary,
            "persona": profile_data.get("persona", {}),
            "user_facts": profile_data.get("user_facts", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/radar")
async def radar(session_id: str):
    """
    获取关系雷达数据
    
    返回当前关系的各项维度评分（如激情、承诺、亲密度、信任度等）。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        radar_data = agent.get_radar(session_id)
        return radar_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def history(session_id: str):
    """
    获取聊天历史记录
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        # Access state manager directly or add a getter in agent
        # Adding a simple getter in agent is cleaner but for now accessing internal state manager via agent if possible
        # Actually agent._state_manager is protected.
        # But I added `_resolve_history` which uses `get_history`.
        # I should double check if I added `get_history` to LoveAgent or just used it internally.
        # I didn't add `get_history` to LoveAgent public API in the last step.
        # However, `_state_manager` is accessible in python.
        # Better: use `agent._state_manager.get_history(session_id)`
        
        history_data = agent._state_manager.get_history(session_id)
        return {"history": history_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/initiative")
async def initiative(session_id: str):
    """
    生成主动搭讪开场白
    
    基于当前的上下文、关系阶段和对方画像，生成适合的主动开启话题的内容。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    try:
        return agent.generate_initiative(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口
    
    接收图片文件，返回 Base64 Data URI，用于在 /chat 接口中作为 image 类型的消息内容发送。
    """
    try:
        content = await file.read()
        # Simple file type check based on extension or header could be added here
        # For now, we assume it's an image and try to guess mime type from filename or default to jpeg
        filename = file.filename or "image.jpg"
        mime_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            mime_type = "image/png"
        elif filename.lower().endswith(".gif"):
            mime_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            mime_type = "image/webp"
            
        base64_encoded = base64.b64encode(content).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{base64_encoded}"
        
        return {"url": data_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    核心聊天接口
    
    处理用户输入，进行多维度分析（情绪、意图、知识检索、策略规划），并生成高情商回复。
    """
    if not agent:
        raise HTTPException(status_code=500, detail="LoveAgent not initialized properly.")
    
    try:
        # Check for image message
        latest_msg = None
        if request.new_message:
            latest_msg = request.new_message
        elif request.messages:
            latest_msg = request.messages[-1]
            
        if latest_msg and latest_msg.type == "image" and latest_msg.url:
            reply_text = agent.handle_image(request.session_id, latest_msg.url)
            return {
                "replies": [{"text": reply_text, "reason": "基于图片内容的视觉理解"}],
                "analysis": {
                    "emotion": {},
                    "topics": ["图片分享"],
                    "persona": {},
                    "strategy": {},
                    "subtext": {} # Initialize empty subtext for image response
                }
            }

        # Convert Pydantic model to dict
        input_data = request.model_dump()
        
        # Call LoveAgent
        result = await agent.generate_replies(input_data)
        
        # Ensure subtext is present in result structure even if agent didn't return it (though agent should)
        if "analysis" in result and "subtext" not in result["analysis"]:
             result["analysis"]["subtext"] = {}
             
        # Debugging
        # print(f"DEBUG SUBTEXT ANALYSIS: {result.get('analysis', {}).get('subtext')}")
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)

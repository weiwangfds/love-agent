import os
import json
import asyncio
import time
from typing import Dict, Any, List
from src.model.qwen_client import QwenClient
from src.analyzers.emotion_analyzer import EmotionAnalyzer
from src.analyzers.persona_profiler import PersonaProfiler
from src.analyzers.search_intent_analyzer import SearchIntentAnalyzer
from src.analyzers.relationship_analyzer import RelationshipAnalyzer
from src.analyzers.topic_analyzer import TopicAnalyzer
from src.analyzers.fact_extractor import FactExtractor
from src.progress.state_manager import StateManager
from src.generation.reply_generator import ReplyGenerator
from src.generation.empathy_engine import EmpathyEngine
from src.generation.initiative_generator import InitiativeGenerator
from src.analyzers.image_analyzer import ImageAnalyzer
from src.analyzers.profile_summarizer import ProfileSummarizer
from src.analyzers.subtext_decoder import SubtextDecoder
from src.analyzers.chat_reviewer import ChatReviewer
from src.progress.opportunity_detector import OpportunityDetector
from src.progress.strategy_planner import StrategyPlanner
from src.progress.feedback_handler import FeedbackHandler
from src.progress.context_awareness import ContextAwareness
from src.vectorstore.chroma_store import ChromaStore
from src.ingestion.history_ingestor import HistoryIngestor
from src.retrieval.retrieval_orchestrator import RetrievalOrchestrator
from src.safety.safety_checker import SafetyChecker


class LoveAgent:
    """
    LoveAgent 核心类
    
    作为整个恋爱辅助系统的中枢，负责协调各个模块的工作：
    1. 接收和处理用户输入（文本/图片）。
    2. 管理会话状态和长期记忆（Vector Store + StateManager）。
    3. 调度各个分析器（情绪、画像、关系、话题等）进行并行分析。
    4. 生成高情商回复和行动建议。
    """
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 LoveAgent
        
        Args:
            config: 配置字典，包含模型配置、路径配置等
        """
        self._client = QwenClient()
        self._model = config.get("model", {}).get("default", "qwen-plus")
        
        # 初始化向量数据库路径
        persist_dir = config.get("chroma", {}).get("persist_directory", "data/chroma")
        self._history_vs = ChromaStore(persist_dir, "history_embeddings") # 历史聊天记录向量库
        self._interest_vs = ChromaStore(persist_dir, "interest_embeddings") # 兴趣点向量库
        self._fact_vs = ChromaStore(persist_dir, "fact_embeddings") # 长期记忆/事实向量库
        
        # 状态持久化管理
        state_dir = config.get("state", {}).get("persist_directory", "data/state")
        self._state_manager = StateManager(state_dir)
        
        # 初始化各个功能模块
        self._ingestor = HistoryIngestor(self._history_vs)
        self._retrieval = RetrievalOrchestrator(self._history_vs)
        self._emotion = EmotionAnalyzer(self._client, self._model)
        self._persona = PersonaProfiler(self._client, self._model)
        self._relationship = RelationshipAnalyzer(self._client, self._model)
        self._topic = TopicAnalyzer(self._client, self._model)
        self._fact_extractor = FactExtractor(self._client, self._model)
        self._search_intent = SearchIntentAnalyzer(self._client, self._model)
        self._planner = StrategyPlanner(self._client, self._model)
        self._reply = ReplyGenerator(self._client, self._model)
        self._empathy = EmpathyEngine(self._client, self._model)
        self._initiative = InitiativeGenerator(self._client, self._model)
        self._safety = SafetyChecker(self._client, self._model)
        self._image_analyzer = ImageAnalyzer(self._client, "qwen-vl-plus") # 使用专门的 VL 模型处理图片
        self._profile_summarizer = ProfileSummarizer(self._client, self._model)
        self._subtext_decoder = SubtextDecoder(self._client, self._model)
        self._chat_reviewer = ChatReviewer(self._client, self._model)
        self._opportunity = OpportunityDetector()
        self._feedback_handler = FeedbackHandler(self._client, self._model)
        self._context_awareness = ContextAwareness()

    def get_radar(self, session_id: str) -> Dict[str, Any]:
        """
        获取指定会话的关系雷达数据
        """
        state = self._state_manager.get_state(session_id)
        return state.get("radar", {})

    def get_profile(self, session_id: str) -> Dict[str, Any]:
        """
        获取指定会话的人物画像和事实标签
        """
        state = self._state_manager.get_state(session_id)
        return {
            "persona": state.get("persona", {}),
            "user_facts": state.get("user_facts", [])
        }

    def _resolve_history(self, chat_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析和合并聊天历史记录
        
        处理传入的消息列表或单条新消息，并与存储的历史记录同步。
        """
        session_id = chat_json.get("session_id", "default")
        incoming_messages = chat_json.get("messages", [])
        new_message = chat_json.get("new_message") 
        
        if new_message:
            # 如果有新消息，追加到状态管理器
            self._state_manager.append_message(session_id, new_message)
            full_history = self._state_manager.get_history(session_id)
        elif incoming_messages:
            # 如果提供了完整列表，更新状态管理器
            self._state_manager.update_state(session_id, {"history": incoming_messages})
            full_history = incoming_messages
        else:
            # 否则直接获取存储的历史
            full_history = self._state_manager.get_history(session_id)
        return full_history

    def _parse_input(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        提取最近的消息用于上下文分析 (默认最近12条)
        """
        window = []
        for m in messages[-12:]:
            window.append({"speaker": m.get("speaker"), "content": m.get("content", "")})
        return window

    def analyze_conversation(self, chat_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        对对话进行基础分析：情绪、机会分值、话题
        """
        window = self._parse_input(chat_json.get("messages", []))
        emotion = self._emotion.analyze(window)
        latest_text = window[-1]["content"] if window else ""
        opp_score = self._opportunity.score(latest_text)
        
        # 动态话题分析
        history_str = ""
        for msg in window[:-1]:
            speaker = "我" if msg["speaker"] == "user" else "对方"
            history_str += f"{speaker}: {msg['content']}\n"
            
        topics = self._topic.analyze(latest_text, history_str)
        
        return {"emotion": emotion, "opportunity_score": opp_score, "topics": topics}

    def search_knowledge(self, topics: List[str], query: str | None = None) -> Dict[str, Any]:
        """
        知识库检索（占位符，可扩展）
        """
        kb_ctx = {"persons": [], "works": [], "topics": topics}
        if query:
            # 标记需要进行在线搜索
            kb_ctx["need_online_search"] = True
            kb_ctx["search_query"] = query
                
        return kb_ctx

    def handle_image(self, session_id: str, image_url: str) -> str:
        """
        处理传入的图片消息
        
        使用 Qwen-VL 模型分析图片内容，并结合当前关系阶段生成回复。
        """
        current_state = self._state_manager.get_state(session_id)
        # 暂时传入空画像，或者从状态加载
        persona = {} 
        
        reply = self._image_analyzer.analyze_and_reply(
            image_url=image_url,
            relationship_stage=current_state.get("relationship_stage", "陌生/破冰"),
            intimacy_level=int(current_state.get("intimacy_level", 1)),
            persona=persona
        )
        return reply

    def generate_profile_summary(self, session_id: str) -> str:
        """
        生成用户画像摘要
        
        基于向量库中存储的事实标签，生成一段通过的文本描述。
        """
        current_state = self._state_manager.get_state(session_id)
        
        # 检索所有相关事实 (限制最近20条以避免 Token 超限)
        # 注意: Chroma 不支持"获取全部"，所以这里使用通用词搜索
        docs = self._fact_vs.similarity_search("用户", n_results=20)
        user_facts = [d["text"] for d in docs]
        
        return self._profile_summarizer.summarize(
            user_facts=user_facts,
            relationship_stage=current_state.get("relationship_stage", "陌生/破冰"),
            intimacy_level=int(current_state.get("intimacy_level", 1))
        )

    def generate_initiative(self, session_id: str) -> Dict[str, Any]:
        """
        主动生成搭讪/开场白
        
        基于当前状态、记忆和环境上下文，生成合适的话题开启对话。
        """
        # 加载状态
        current_state = self._state_manager.get_state(session_id)
        
        # 加载相关事实 (获取最近5条作为上下文)
        # 在真实系统中可以根据"兴趣"或"习惯"进行语义检索
        docs = self._fact_vs.similarity_search("用户喜好 习惯", n_results=5)
        user_facts = [d["text"] for d in docs]
        
        # 加载画像
        persona = current_state.get("persona", {})
        
        last_updated_ts = current_state.get("last_updated", 0)
        import datetime
        last_chat_time = datetime.datetime.fromtimestamp(last_updated_ts).strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取实时上下文 (天气、节日等)
        env_context = self._context_awareness.get_context()
        env_str = env_context.get("context_str", "")
        
        return self._initiative.generate(
            relationship_stage=current_state.get("relationship_stage", "陌生/破冰"),
            intimacy_level=int(current_state.get("intimacy_level", 1)),
            persona=persona,
            user_facts=user_facts,
            last_chat_time=last_chat_time,
            environment_context=env_str
        )

    async def handle_feedback(self, session_id: str, user_feedback: str, last_agent_reply: str) -> Dict[str, Any]:
        """
        处理用户对 Agent 回复的反馈
        """
        current_state = self._state_manager.get_state(session_id)
        
        # 运行反馈分析
        loop = asyncio.get_running_loop()
        analysis = await loop.run_in_executor(
            None, 
            self._feedback_handler.analyze,
            user_feedback,
            last_agent_reply,
            current_state
        )
        
        # 如果需要调整策略，可以在这里更新状态
        return analysis

    async def review_chat(self, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        复盘聊天记录
        
        分析给定的聊天历史，识别高光时刻和扣分项。
        """
        history_str = ""
        for msg in chat_history:
            speaker = "我" if msg.get("speaker") == "user" else "对方"
            content = msg.get("content", "")
            history_str += f"{speaker}: {content}\n"
        
        # 在执行器中运行以避免阻塞
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._chat_reviewer.review, history_str)

    async def process_uploaded_history(self, session_id: str, uploaded_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理上传的聊天记录:
        1. 合并现有历史 (去重)
        2. 更新状态
        3. 存入向量数据库
        4. 基于最近上下文触发画像和雷达更新
        """
        # 1. 合并 & 去重
        new_messages = self._state_manager.merge_history(session_id, uploaded_messages)
        
        if not new_messages:
            return {"status": "no_new_messages", "message": "没有新的消息需要处理。"}
            
        # 获取完整的更新后的历史用于上下文分析
        full_history = self._state_manager.get_history(session_id)
        
        # 2. 存入向量库 (仅新消息)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._ingestor.ingest, {"session_id": session_id, "messages": new_messages})
        
        # 3. 触发分析 (画像, 雷达, 事实)
        # 我们分析 *最新* 的上下文来更新 *当前* 状态。
        
        # 构建上下文 (最近20条)
        window_size = 20
        recent_msgs = full_history[-window_size:]
        
        # 解析用于分析器
        parsed_window = [{"speaker": m.get("speaker"), "content": m.get("content", "")} for m in recent_msgs]
        
        # 构建历史字符串用于关系/事实分析
        history_str = ""
        for msg in recent_msgs:
            speaker = "我" if msg.get("speaker") == "user" else "对方"
            history_str += f"{speaker}: {msg.get('content', '')}\n"
            
        latest_text = parsed_window[-1]["content"] if parsed_window else ""
        
        current_state = self._state_manager.get_state(session_id)

        # 定义并行任务
        t_persona = loop.run_in_executor(None, self._persona.profile, parsed_window)
        t_rel = loop.run_in_executor(None, self._relationship.update_state, history_str, current_state)
        t_facts = loop.run_in_executor(None, self._fact_extractor.extract, latest_text, history_str)
        
        # 并行运行
        persona_res, rel_update, new_facts = await asyncio.gather(t_persona, t_rel, t_facts)
        
        # 更新状态
        updates = {}
        if persona_res:
            updates["persona"] = persona_res
        if rel_update:
            updates.update(rel_update)
        
        if new_facts:
            # 将事实存入向量库
            import time
            ids = [f"fact_{session_id}_{int(time.time())}_{i}" for i in range(len(new_facts))]
            metadatas = [{"session_id": session_id, "timestamp": time.time(), "type": "user_fact"} for _ in new_facts]
            self._fact_vs.add_texts(ids, new_facts, metadatas)
            
            # 更新状态中的事实列表
            current_facts = current_state.get("user_facts", [])
            for f in new_facts:
                if f not in current_facts:
                    current_facts.append(f)
            updates["user_facts"] = current_facts
            
        if updates:
            self._state_manager.update_state(session_id, updates)
            
        return {
            "status": "success", 
            "new_messages_count": len(new_messages),
            "total_messages_count": len(full_history),
            "updates": updates
        }

    async def generate_replies(self, chat_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成回复的核心流程
        """
        # 0. 解析历史 & 输入
        full_history = self._resolve_history(chat_json)
        
        # 准备任务上下文
        task_context = chat_json.copy()
        task_context["messages"] = full_history
        if "new_message" in task_context:
            del task_context["new_message"]

        window = self._parse_input(full_history)
        latest_text = window[-1]["content"] if window else ""
        
        # 准备历史字符串
        history_str = ""
        for msg in window:
            speaker = "我" if msg["speaker"] == "user" else "对方"
            history_str += f"{speaker}: {msg['content']}\n"
            
        session_id = task_context.get("session_id", "default")
        loop = asyncio.get_running_loop()

        # 1. 并行任务组 1: 分析 & 数据获取
        # 任务: 摄入, 分析(情绪/话题), 事实提取, 意图, 画像, 检索(历史), 检索(事实), 关系更新
        
        # T1: 消息摄入 (存入向量库)
        t_ingest = loop.run_in_executor(None, self._ingestor.ingest, task_context)
        
        # T2: 基础分析 (情绪, 机会, 话题)
        t_analyze = loop.run_in_executor(None, self.analyze_conversation, task_context)
        
        # T3: 事实提取 (副作用：更新向量库和状态)
        def _extract_and_store_facts():
            new_facts = self._fact_extractor.extract(latest_text, history_str)
            if new_facts:
                import time
                ids = [f"fact_{session_id}_{int(time.time())}_{i}" for i in range(len(new_facts))]
                metadatas = [{"session_id": session_id, "timestamp": time.time(), "type": "user_fact"} for _ in new_facts]
                self._fact_vs.add_texts(ids, new_facts, metadatas)
                # 更新状态中的事实
                current_facts = self._state_manager.get_state(session_id).get("user_facts", [])
                for f in new_facts:
                    if f not in current_facts:
                        current_facts.append(f)
                self._state_manager.update_state(session_id, {"user_facts": current_facts})
            return new_facts
        t_facts = loop.run_in_executor(None, _extract_and_store_facts)
        
        # T4: 搜索意图分析
        t_intent = loop.run_in_executor(None, self._search_intent.analyze, latest_text, history_str)
        
        # T5: 画像更新
        def _profile_and_store():
            p = self._persona.profile(window)
            if p:
                self._state_manager.update_persona(session_id, p)
            return p
        t_persona = loop.run_in_executor(None, _profile_and_store)
        
        # T6: 历史检索
        t_retrieval_agg = loop.run_in_executor(None, self._retrieval.aggregate, latest_text)
        
        # T7: 事实检索
        def _retrieve_facts():
            relevant = []
            # 检索经验教训
            lesson_docs = self._fact_vs.similarity_search("用户偏好调整 策略教训", n_results=3, where={"type": "strategy_lesson"})
            relevant.extend([d["text"] for d in lesson_docs])
            # Contextual
            if latest_text:
                docs = self._fact_vs.similarity_search(latest_text, n_results=3)
                existing = set(relevant)
                for d in docs:
                    if d["text"] not in existing:
                        relevant.append(d["text"])
            return relevant
        t_fact_retrieval = loop.run_in_executor(None, _retrieve_facts)
        
        # T8: Relationship Update
        current_state = self._state_manager.get_state(session_id)
        provided_stage = task_context.get("relationship_stage")
        
        def _update_relationship():
            if not provided_stage:
                return self._relationship.update_state(history_str, current_state)
            return {}
        t_rel_update = loop.run_in_executor(None, _update_relationship)
 
        # Await Group 1
        (
            _, 
            analysis_res, 
            _, 
            intent_res,
            persona_res,
            retrieval_ctx,
            relevant_facts,
            rel_update_info
        ) = await asyncio.gather(
            t_ingest, t_analyze, t_facts, t_intent, t_persona, t_retrieval_agg, t_fact_retrieval, t_rel_update
        )
 
        # Update State
        radar_data = {}
        overall_analysis = ""
        if rel_update_info:
            current_state.update(rel_update_info)
            radar_data = rel_update_info.get("radar", {})
            overall_analysis = rel_update_info.get("overall_analysis", "")
            loop.run_in_executor(None, self._state_manager.update_state, session_id, current_state)
 
        # Determine Relationship Parameters
        relationship_stage = provided_stage or current_state.get("relationship_stage", "陌生/破冰")
        provided_intimacy = task_context.get("intimacy_level")
        intimacy_level = int(provided_intimacy) if provided_intimacy is not None else int(current_state.get("intimacy_level", 1))
        
        # Fallback for missing relationship info
        if not all([relationship_stage, intimacy_level is not None]) or not radar_data:
            # Quick sync fallback if update didn't work or wasn't called or radar missing
            rel_analysis = await loop.run_in_executor(None, self._relationship.analyze, history_str)
            relationship_stage = rel_analysis.get("relationship_stage", "陌生/破冰")
            intimacy_level = rel_analysis.get("intimacy_level", 1)
            radar_data = rel_analysis.get("radar", {})
            overall_analysis = rel_analysis.get("overall_analysis", "")
            # Also save this fallback analysis to state
            self._state_manager.update_state(session_id, {
                "relationship_stage": relationship_stage,
                "intimacy_level": intimacy_level,
                "radar": radar_data,
                "overall_analysis": overall_analysis
            })

        # 2. Parallel Task Group 2: Subtext & Conditional Search & Planning
        
        # T9: Subtext Decoding
        t_subtext = loop.run_in_executor(None, self._subtext_decoder.decode, latest_text, history_str, relationship_stage)
        
        # T10: Search Knowledge
        async def _search_task():
            if intent_res.get("need_search"):
                query = intent_res.get("search_keywords")
                return await loop.run_in_executor(None, self.search_knowledge, analysis_res.get("topics", []), query)
            return self.search_knowledge(analysis_res.get("topics", []))
        t_search = _search_task()

        # T11: Planning
        provided_humor = task_context.get("humor_level")
        humor_level = int(provided_humor) if provided_humor is not None else 3
        current_appellation = task_context.get("current_appellation") or current_state.get("current_appellation", "你")
        user_gender = task_context.get("user_gender") or "未知"
        target_gender = task_context.get("target_gender") or "未知"
        
        t_planner = loop.run_in_executor(None, self._planner.plan, 
            persona_res, 
            analysis_res.get("emotion", {}),
            relationship_stage,
            intimacy_level,
            humor_level,
            current_appellation,
            user_gender,
            target_gender,
            history_str
        )
        
        subtext_res, kb_ctx, planner_out = await asyncio.gather(t_subtext, t_search, t_planner)
        
        # 3. Task Group 3: Post-Planning Processing
        reply_strategy = planner_out.get("reply_strategy") or "温柔体贴"
        language_style = planner_out.get("language_style") or "生活化、自然"
        topic_management = planner_out.get("topic_management") or {}
        boundary_assessment = planner_out.get("boundary_assessment") or {}
        app_update = planner_out.get("appellation_update") or {}
        action_guide = planner_out.get("action_guide") or {}
        
        if app_update.get("should_update"):
            current_appellation = app_update.get("new_appellation") or current_appellation
            # Update appellation in state
            self._state_manager.update_state(session_id, {"current_appellation": current_appellation})

        # 4. Task Group 4: Generation & Safety
        emotion_label = analysis_res.get("emotion", {}).get("emotion", "neutral")
        
        async def _generate_and_check_safety(is_retry=False, temp=None):
            if emotion_label == "negative" and not is_retry:
                # First attempt for negative emotion uses EmpathyEngine
                import functools
                print(f"DEBUG: Calling EmpathyEngine with persona keys: {list(persona_res.keys()) if persona_res else 'None'}, facts count: {len(relevant_facts) if relevant_facts else 0}")
                aid = await loop.run_in_executor(None, functools.partial(
                    self._empathy.generate,
                    target_message=latest_text,
                    current_emotion=emotion_label,
                    emotion_score=int(analysis_res.get("emotion", {}).get("detail", {}).get("emotion_score", 4) or 4),
                    relationship_stage=relationship_stage,
                    persona=persona_res,
                    user_facts=relevant_facts
                ))
                candidates = aid.get("replies") or []
            elif emotion_label == "negative" and is_retry:
                # Retry for negative uses EmpathyEngine with higher temp
                import functools
                aid = await loop.run_in_executor(None, functools.partial(
                    self._empathy.generate,
                    target_message=latest_text,
                    current_emotion=emotion_label,
                    emotion_score=int(analysis_res.get("emotion", {}).get("detail", {}).get("emotion_score", 4) or 4),
                    relationship_stage=relationship_stage,
                    persona=persona_res,
                    user_facts=relevant_facts,
                    temperature=temp or 0.9
                ))
                candidates = aid.get("replies") or []
            else:
                # Normal generation
                kwargs = {
                    "target_message": latest_text,
                    "relationship_stage": relationship_stage,
                    "intimacy_level": intimacy_level,
                    "humor_level": humor_level,
                    "reply_strategy": reply_strategy,
                    "language_style": language_style,
                    "current_appellation": current_appellation,
                    "kb_context": kb_ctx,
                    "retrieval_context": retrieval_ctx,
                    "user_gender": user_gender,
                    "target_gender": target_gender,
                    "topic_management": topic_management,
                    "boundary_assessment": boundary_assessment,
                    "action_guide": action_guide,
                    "user_facts": relevant_facts,
                }
                if temp:
                    kwargs["temperature"] = temp
                    
                import functools
                gen = await loop.run_in_executor(None, functools.partial(self._reply.generate, **kwargs))
                candidates = gen.get("replies") or []
            
            valid_replies = []
            for r in candidates:
                text = r.get("text") or ""
                risk = await loop.run_in_executor(None, self._safety.check, text)
                if not (risk.get("safety_risk") or risk.get("emergency_brake")):
                    valid_replies.append(r)
            return valid_replies

        safe_replies = await _generate_and_check_safety()
        
        if not safe_replies:
            # Retry with higher temperature / different engine
            safe_replies = await _generate_and_check_safety(is_retry=True, temp=1.0)

        ret = {
            "replies": safe_replies[:6],
            "analysis": {
                "emotion": analysis_res.get("emotion"),
                "topics": analysis_res.get("topics", []),
                "persona": persona_res,
                "strategy": planner_out,
                "kb_context": kb_ctx, 
                "search_intent": intent_res, 
                "facts": relevant_facts, 
                "subtext": subtext_res, 
                "radar": radar_data,
                "overall_analysis": overall_analysis,
                "action_guide": action_guide,
            },
        }
        return ret


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        import yaml
        return yaml.safe_load(f)

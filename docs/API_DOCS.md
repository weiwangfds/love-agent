# Love Agent API 文档

Love Agent 提供了一套 RESTful API，支持与前端应用（如 Web、App、小程序）进行交互。

## 基础信息

- **默认端口**: `8090`
- **基础 URL**: `http://localhost:8090`
- **协议**: HTTP/1.1
- **数据格式**: JSON

## 快速开始

启动服务器：

```bash
# 在项目根目录下运行
bash scripts/run_server.sh
# 或者
python3 src/server.py
```

---

## 接口列表

### 1. 聊天对话 (Chat)

核心接口，用于发送消息并获取智能回复。支持增量更新（仅发送最新消息）或全量上下文发送。

- **URL**: `/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### 请求参数 (Request Body)

| 字段 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `session_id` | string | 是 | 会话唯一标识符，用于状态保持和记忆检索。 |
| `new_message` | object | 否 | 最新的一条消息（推荐使用此方式，系统会自动拼接历史）。 |
| `messages` | array | 否 | 完整的消息历史列表。如果提供了 `new_message`，此字段可选；否则必须包含至少一条消息。 |
| `relationship_stage` | string | 否 | 关系阶段（如：破冰、暧昧、热恋、冷淡）。不传则自动推断或沿用之前的状态。 |
| `intimacy_level` | int | 否 | 亲密度等级 (0-10)。不传则自动推断。 |
| `user_gender` | string | 否 | 用户性别（"男"/"女"）。 |
| `target_gender` | string | 否 | 对方性别（"男"/"女"）。 |

**Message 对象结构**:
```json
{
  "speaker": "user" | "target",  // "user": 我方, "target": 对方
  "content": "消息内容",
  "type": "text" | "image",      // 默认为 text
  "url": "http://..."            // 图片URL (当 type="image" 时必填)
}
```

#### 请求示例 (增量模式 - 推荐)
```json
{
  "session_id": "session_123",
  "new_message": {
    "speaker": "target",
    "content": "今天好累啊，不想动。"
  }
}
```

#### 响应参数 (Response)

```json
{
  "replies": [
    {
      "text": "抱抱，是工作太忙了吗？今晚早点休息吧。",
      "reason": "表达关心与共情"
    }
  ],
  "analysis": {
    "emotion": { "emotion": "fatigue", ... },
    "topics": ["工作压力"],
    "radar": { "passion": 3, "intimacy": 5, "commitment": 2 }, // 实时关系雷达
    "action_guide": { ... } // 行动建议
  }
}
```

---

### 2. 获取聊天历史 (Get History)

获取指定会话的所有历史记录。

- **URL**: `/history`
- **Method**: `GET`
- **Query Params**:
  - `session_id`: string (必填)

#### 响应示例
```json
{
  "history": [
    { "speaker": "user", "content": "在吗？", "timestamp": 1712345678 },
    { "speaker": "target", "content": "在的，怎么啦？", "timestamp": 1712345690 }
  ]
}
```

---

### 3. 获取用户画像 (Get Profile)

获取基于过往对话生成的对方画像摘要及提取的事实标签。

- **URL**: `/profile`
- **Method**: `GET`
- **Query Params**:
  - `session_id`: string (必填)

#### 响应示例
```json
{
  "summary": "对方是一个性格内向但心思细腻的人，喜欢摄影和猫...",
  "persona": {
    "mbti": "INFP",
    "keywords": ["敏感", "文艺"]
  },
  "user_facts": [
    "喜欢喝拿铁",
    "周五晚上通常有空",
    "讨厌吃香菜"
  ]
}
```

---

### 4. 获取关系雷达 (Get Radar)

获取当前关系的各项维度评分（如激情、承诺、亲密度、信任度等）。

- **URL**: `/radar`
- **Method**: `GET`
- **Query Params**:
  - `session_id`: string (必填)

#### 响应示例
```json
{
  "passion": 4,        // 激情
  "intimacy": 6,       // 亲密
  "commitment": 3,     // 承诺
  "trust": 7,          // 信任
  "communication": 8   // 沟通
}
```

---

### 5. 聊天复盘 (Chat Review)

对一段聊天记录进行深度复盘，分析高光时刻和扣分项。

- **URL**: `/review`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
  "messages": [
    { "speaker": "user", "content": "..." },
    { "speaker": "target", "content": "..." }
  ]
}
```

#### 响应示例
```json
{
  "score": 85,
  "summary": "整体互动良好，情绪价值提供到位。",
  "highlights": [
    { "content": "...", "reason": "幽默化解了尴尬" }
  ],
  "lowlights": [
    { "content": "...", "reason": "在此处显得过于急切", "suggestion": "可以试着..." }
  ]
}
```

---

### 6. 主动搭讪生成 (Initiative)

在冷场或需要开启新话题时，生成主动搭讪的开场白。

- **URL**: `/initiative`
- **Method**: `GET`
- **Query Params**:
  - `session_id`: string (必填)

#### 响应示例
```json
{
  "content": "对了，之前你说想看的那个展，这周末好像是最后一天了？",
  "strategy": "利用共同兴趣开启话题"
}
```

---

### 7. 图片上传 (Upload Image)

上传图片以获取 URL (Base64 Data URI)，用于在 Chat 接口中发送图片消息。

- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### 请求参数
- `file`: binary (图片文件)

#### 响应示例
```json
{
  "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

---

### 8. 反馈 (Feedback)

对 Agent 的回复进行反馈（点赞/点踩），用于优化后续回复。

- **URL**: `/feedback`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
  "session_id": "session_123",
  "original_reply": "Agent生成的回复内容",
  "feedback_type": "like" | "dislike",
  "reason": "可选的反馈理由"
}
```

---

### 9. 导入聊天记录 (Ingest History)

批量导入聊天历史记录，支持去重和自动分析。系统会合并新消息，并基于更新后的历史触发用户画像和关系状态的更新。

- **URL**: `/upload_history`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "speaker": "user",
      "content": "之前的聊天记录...",
      "timestamp": 1712345000
    },
    {
      "speaker": "target",
      "content": "是的，这是之前的。",
      "timestamp": 1712345010
    }
  ]
}
```

#### 响应示例
```json
{
  "status": "success",
  "new_messages_count": 2,
  "total_messages_count": 50,
  "updates": {
    "persona": { ... },
    "radar": { ... }
  }
}
```

---

### 9. 上传聊天记录 (Upload History)

批量上传聊天记录，系统会自动去重、排序，并更新用户画像和关系状态。

- **URL**: `/upload_history`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "speaker": "user",
      "content": "之前的聊天记录1",
      "timestamp": 1712340000
    },
    {
      "speaker": "target",
      "content": "之前的聊天记录2",
      "timestamp": 1712340010
    }
  ]
}
```

#### 响应示例
```json
{
  "status": "success",
  "new_messages_count": 5,
  "total_messages_count": 100,
  "updates": {
    "persona": { ... },
    "radar": { ... }
  }
}
```

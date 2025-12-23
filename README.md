# Love Agent (恋爱高情商辅助助手)

Love Agent 是一个基于大语言模型（LLM）的情感互动辅助系统。它不仅仅是一个聊天机器人，而是一个"情感军师"，旨在通过深度分析对话上下文、双方人设、情绪状态，提供高情商、有策略的回复建议，帮助用户在亲密关系中自然推进、化解矛盾或增进感情。

## 核心功能

1.  **深度情感分析**：
    *   识别主导情绪（如焦虑、期待、失望）。
    *   分析潜在需求（情感需求 vs 解决问题）。
    *   构建对方性格画像（MBTI、依恋类型、沟通风格）。

2.  **动态策略规划**：
    *   **话题管理**：自动检测话题是否枯竭，提供自然的话题切换技巧。
    *   **边界判断**：识别不合理要求或知识盲区，建议拒绝或真诚请教。
    *   **关系推进**：捕捉情感窗口，建议升级关系或进行邀约。
    *   **适度斗嘴/打趣**：在暧昧期或轻松氛围下，生成推拉式玩笑以拉近距离。

3.  **多场景支持**：
    *   覆盖破冰、暧昧、热恋、冲突、冷场修复、深度焦虑等多种现实场景。
    *   针对不同性别（男对女、女对男）调整语言风格（保护欲 vs 撒娇/崇拜）。

4.  **知识增强**：
    *   集成轻量级本地知识库（如电影、音乐信息），在对话中自动检索相关实体，丰富回复内容。

## 快速开始

### 1. 环境准备

确保您的 Python 版本 >= 3.10。

```bash
# 克隆项目（假设您已下载代码）
cd love-agent

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

本项目默认使用阿里通义千问（Qwen）模型。您需要设置环境变量 `DASHSCOPE_API_KEY`。

```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

### 3. 配置文件

核心配置位于 `config/config.yaml`：

```yaml
model:
  default: qwen-plus  # 默认使用的模型
  fallback: qwen3-max # 备用模型
kb:
  path: data/kb/base.json # 本地知识库路径
```

## 使用指南

### 运行单个场景测试

项目在 `data/examples/` 目录下提供了多种预设的对话场景（JSON格式）。

**运行命令：**

```bash
# 必须设置 PYTHONPATH=. 以便正确导入模块
PYTHONPATH=. python3 scripts/run_agent.py data/examples/ice_breaking.json
```

**示例输出：**

```json
{
  "replies": [
    { "text": "你好呀，头像很有艺术感呢", "reason": "建立联系" },
    ...
  ],
  "analysis": { ... }
}
```

### 批量测试与生成报告

您可以一次性运行所有场景并生成 Markdown 格式的测试报告：

```bash
PYTHONPATH=. python3 scripts/generate_report.py
```

运行后查看 `TEST_REPORT.md`，其中包含了每个场景的详细分析、策略判断和生成的回复。

## 输入数据格式

输入 JSON 文件结构如下（示例）：

```json
{
  "session_id": "test_session",
  "relationship_stage": "暧昧期",
  "intimacy_level": 5,     // 0-10
  "humor_level": 3,        // 0-5
  "current_appellation": "你",
  "user_gender": "男",     // 用户性别
  "target_gender": "女",   // 对方性别
  "messages": [
    { 
      "speaker": "target", // 对方说话
      "content": "今天好累啊..." 
    },
    {
      "speaker": "user",   // 我方说话（历史记录）
      "content": "抱抱，怎么啦？"
    },
    {
      "speaker": "target", // 对方最新回复（待回复的消息）
      "content": "被老板骂了一顿，气死我了"
    }
  ]
}
```

## 项目结构

```
.
├── config/             # 配置文件
├── data/
│   ├── examples/       # 测试场景用例
│   └── kb/             # 本地知识库
├── scripts/            # 运行脚本
├── src/
│   ├── analyzers/      # 情绪与人设分析器
│   ├── generation/     # 回复生成与共情引擎
│   ├── knowledge/      # 知识库服务
│   ├── model/          # LLM 客户端
│   ├── progress/       # 策略规划器
│   ├── prompts/        # Prompt 模板管理
│   └── love_agent.py   # 主程序入口
└── requirements.txt    # 依赖列表
```

## 开发扩展

*   **添加新场景**：在 `data/examples/` 下新建 JSON 文件。
*   **修改提示词**：主要 Prompt 定义在 `src/prompts/prompts.py`。
*   **扩展知识库**：编辑 `data/kb/base.json` 添加更多电影、音乐或话题标签。

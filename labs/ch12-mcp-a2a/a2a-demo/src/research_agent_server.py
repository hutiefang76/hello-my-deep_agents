"""Case 3 · A2A Agent Server — 提供"研究员 Agent"能力, 可被其他 Agent 通过 A2A 调用.

A2A 协议核心:
  1. Agent Card (/.well-known/agent-card.json) — 公开自身身份+能力
  2. Task (POST /a2a/v1/tasks) — 接其他 Agent 的工作请求
  3. Message — Task 内的对话消息
  4. Artifact — Task 产出物

跑法:
    pip install fastapi uvicorn pydantic
    python src/research_agent_server.py
    # 起在 http://localhost:9000
    # Agent Card: http://localhost:9000/.well-known/agent-card.json
"""

from __future__ import annotations

import sys
import time
import uuid
from typing import Any
from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ============================================================
# A2A 协议数据模型 (简化版, 对齐 a2a-protocol.org spec)
# ============================================================


class MessagePart(BaseModel):
    """消息片段 — A2A 消息可由多个 part 组成 (text/file/image)."""
    type: str = "text"  # "text" | "file" | "image"
    text: str | None = None
    mime_type: str | None = None


class Message(BaseModel):
    """A2A 消息 — Task 内的一次发言."""
    role: str  # "user" | "agent"
    parts: list[MessagePart]


class TaskSubmit(BaseModel):
    """提交 Task 请求体."""
    message: Message
    context_id: str | None = None  # 多轮会话上下文 ID


class Artifact(BaseModel):
    """Task 产出物."""
    name: str
    content: str
    mime_type: str = "text/plain"


class Task(BaseModel):
    """A2A Task — 一次工作单元, 有完整 lifecycle."""
    id: str
    context_id: str
    status: str  # submitted | working | completed | failed
    messages: list[Message] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)


# ============================================================
# Agent 实现 (实际可换成 LangGraph / DeepAgents / 任何框架)
# ============================================================


class ResearchAgent:
    """模拟一个研究员 Agent — 接 query, 返回研究报告.

    真业务里这层可以接 Tavily 搜索 + LLM 总结.
    本 demo 用模板返回, 突出 A2A 协议本身.
    """

    def handle(self, query: str) -> str:
        """处理 query, 返回研究报告."""
        return f"""# 研究报告: {query}

## 关键发现
1. {query} 在 2025 年成为热点
2. 主流方案是 X、Y、Z
3. 最佳实践: A、B、C

## 数据
- 市场规模: $XX 亿
- 年增速: XX%
- 头部玩家: ABC

(本报告由 ResearchAgent 自动生成, 时间: {time.strftime('%Y-%m-%d %H:%M')})
"""


# ============================================================
# A2A Server (FastAPI)
# ============================================================

app = FastAPI(title="Research Agent (A2A)")
agent = ResearchAgent()
_tasks: dict[str, Task] = {}
_lock = Lock()


@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    """A2A 协议核心 — 公开 Agent 身份 + 能力 + endpoint.

    其他 Agent 通过这个 URL 发现你, 决定要不要调你.
    URL path 必须是 /.well-known/agent-card.json (协议规定).
    """
    return {
        "name": "Research Agent",
        "version": "0.1.0",
        "description": "给 query 生成结构化研究报告. 适合做调研类 Agent 协作.",
        "url": "http://localhost:9000",
        "capabilities": {
            "streaming": False,
            "push_notifications": False,
        },
        "skills": [
            {
                "id": "research",
                "name": "研究查询",
                "description": "接受研究问题, 返回结构化研究报告",
                "input_modes": ["text"],
                "output_modes": ["text", "markdown"],
            }
        ],
        "default_input_modes": ["text"],
        "default_output_modes": ["text"],
    }


@app.post("/a2a/v1/tasks")
def submit_task(req: TaskSubmit) -> Task:
    """A2A 协议 — 提交 Task. 这是其他 Agent 调你的入口."""
    # 提取用户消息文本
    text_parts = [p.text for p in req.message.parts if p.type == "text" and p.text]
    if not text_parts:
        raise HTTPException(400, "Empty text in message")
    query = " ".join(text_parts)

    # 创建 Task
    task = Task(
        id=str(uuid.uuid4()),
        context_id=req.context_id or str(uuid.uuid4()),
        status="working",
        messages=[req.message],
    )

    # 处理 (真业务里这里可以 async 长跑, 先返 working, 后续 update)
    try:
        report = agent.handle(query)
        task.artifacts.append(
            Artifact(name="research_report.md", content=report, mime_type="text/markdown")
        )
        task.messages.append(
            Message(role="agent", parts=[MessagePart(type="text", text="研究完毕, 见 artifact")])
        )
        task.status = "completed"
    except Exception as e:
        task.status = "failed"
        task.messages.append(
            Message(role="agent", parts=[MessagePart(type="text", text=f"失败: {e}")])
        )

    # 存 (真业务用 DB / Redis)
    with _lock:
        _tasks[task.id] = task

    return task


@app.get("/a2a/v1/tasks/{task_id}")
def get_task(task_id: str) -> Task:
    """A2A 协议 — 查询 Task 状态. 异步任务靠这个轮询."""
    with _lock:
        task = _tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.get("/")
def root() -> dict[str, str]:
    """欢迎页, 引导到 agent card."""
    return {
        "name": "Research Agent",
        "agent_card": "http://localhost:9000/.well-known/agent-card.json",
        "submit_task": "POST /a2a/v1/tasks",
        "get_task": "GET /a2a/v1/tasks/{task_id}",
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    import uvicorn
    print("=" * 60)
    print(" A2A Research Agent Server")
    print("=" * 60)
    print(" Agent Card: http://localhost:9000/.well-known/agent-card.json")
    print(" Submit:     POST http://localhost:9000/a2a/v1/tasks")
    print(" Validate:   python src/agent_client.py")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=9000)


if __name__ == "__main__":
    main()

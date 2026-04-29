"""Case 3 验证 · A2A Client — 模拟"另一个 Agent"通过 A2A 协议调研究员 Agent.

完整 4 步演示 A2A:
    1. 发现 Agent: GET /.well-known/agent-card.json
    2. 决策: 看 Agent 的 skills 是否匹配需求
    3. 提交 Task: POST /a2a/v1/tasks
    4. 取 Task 结果 (含 artifacts)

跑法 (先起 server, 见 research_agent_server.py):
    python src/agent_client.py
"""

from __future__ import annotations

import json
import sys

import httpx

REMOTE_AGENT_URL = "http://localhost:9000"


def discover_agent(base_url: str) -> dict:
    """Step 1 · 发现 Agent — 拉 Agent Card."""
    r = httpx.get(f"{base_url}/.well-known/agent-card.json", timeout=5)
    r.raise_for_status()
    return r.json()


def submit_task(base_url: str, query: str) -> dict:
    """Step 3 · 提交 Task."""
    payload = {
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": query}],
        },
        "context_id": "demo-session-001",
    }
    r = httpx.post(
        f"{base_url}/a2a/v1/tasks", json=payload, timeout=30
    )
    r.raise_for_status()
    return r.json()


def get_task(base_url: str, task_id: str) -> dict:
    """Step 4 · 查 Task 详情."""
    r = httpx.get(f"{base_url}/a2a/v1/tasks/{task_id}", timeout=5)
    r.raise_for_status()
    return r.json()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print(" A2A Client Demo — 跨 Agent 调用流程")
    print("=" * 60)

    # Step 1: 发现
    print("\n[1] 发现 remote agent (GET /.well-known/agent-card.json)")
    try:
        card = discover_agent(REMOTE_AGENT_URL)
    except httpx.HTTPError as e:
        print(f"   ❌ 发现失败 (server 没起?): {e}")
        print(f"   先在另一个 terminal 跑: python src/research_agent_server.py")
        sys.exit(1)

    print(f"   Agent 名称: {card['name']} v{card['version']}")
    print(f"   描述:      {card['description']}")
    print(f"   skills:    {[s['id'] for s in card['skills']]}")

    # Step 2: 决策 — 看 skills 是否匹配
    print("\n[2] 决策: 我需要 'research' skill, 这个 agent 有吗?")
    has_research = any(s["id"] == "research" for s in card["skills"])
    print(f"   匹配: {has_research} ✓" if has_research else "   不匹配 ✗")
    if not has_research:
        sys.exit(1)

    # Step 3: 提交 Task
    query = "MCP 协议在 2026 年的发展趋势"
    print(f"\n[3] 提交 Task: '{query}'")
    task = submit_task(REMOTE_AGENT_URL, query)
    print(f"   Task ID:  {task['id']}")
    print(f"   状态:     {task['status']}")
    print(f"   产出物:   {len(task['artifacts'])} 个 artifact")

    # Step 4: 看产出物 (本 demo 是同步, 所以提交时已 completed)
    if task["status"] == "completed":
        print("\n[4] 拿研究报告:")
        for a in task["artifacts"]:
            print(f"\n   --- {a['name']} ({a['mime_type']}) ---")
            print(a["content"][:500] + ("..." if len(a["content"]) > 500 else ""))
    else:
        # 异步轮询 (本 demo 用不到, 但展示标准模式)
        print("\n[4] 异步轮询 (生产场景)...")
        while task["status"] in ("submitted", "working"):
            import time
            time.sleep(1)
            task = get_task(REMOTE_AGENT_URL, task["id"])
            print(f"   状态: {task['status']}")

    print("\n" + "=" * 60)
    print(" ✅ A2A 协议四步走完成")
    print("    1) 发现  2) 决策  3) 提交 Task  4) 拿 artifact")
    print("=" * 60)


if __name__ == "__main__":
    main()

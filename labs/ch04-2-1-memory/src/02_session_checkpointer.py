"""02 · 会话记忆 — LangGraph Checkpointer.

短期记忆只能在一次 invoke 内, 一旦程序重启或换 thread 就丢.
Checkpointer 把每一步的 state (含 messages) 持久化到 DB, 重启/恢复都能续上.

本 lab 用 SqliteSaver 写本地 .db 文件 — 教学场景最简单, 真实项目可换 PostgresSaver / RedisSaver.

教学要点:
    1. SqliteSaver.from_conn_string("file.db")
    2. config={"configurable": {"thread_id": "xxx"}} 区分不同会话
    3. 第二次 invoke 同 thread_id 时, 自动加载上次状态

Run:
    python 02_session_checkpointer.py

注: 跑完会在当前目录留一个 _memory.db, verify.sh 会清理.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.checkpoint.sqlite import SqliteSaver  # noqa: E402


DB_PATH = Path(__file__).parent / "_memory.db"


def build_agent_with_checkpointer():
    """构造带 Checkpointer 的 DeepAgent."""
    # SqliteSaver 接受 sqlite3 connection
    import sqlite3

    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    agent = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt="你是简短回复的助手, 每次回答不超过 50 字. 记住用户告诉你的信息.",
        checkpointer=checkpointer,
    )
    return agent, conn


def chat(agent, thread_id: str, user_msg: str) -> str:
    """带 thread_id 的对话 — 同 thread 自动续上下文."""
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_msg)]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 10},
    )
    return result["messages"][-1].content


def main() -> None:
    print("=" * 60)
    print("Ch4.2.1 · 02 会话记忆 (SqliteSaver Checkpointer)")
    print("=" * 60)

    # 清掉旧 db, 保证可复现
    if DB_PATH.exists():
        DB_PATH.unlink()
    print(f"DB 路径: {DB_PATH}")

    agent, conn = build_agent_with_checkpointer()

    # === 场景 1: alice 的会话 ===
    print("\n--- thread_id='alice' 第 1 轮 ---")
    r1 = chat(agent, "alice", "你好, 我叫 Alice, 我是 Java 工程师.")
    print(f"AI: {r1}")

    print("\n--- thread_id='alice' 第 2 轮 (新 invoke 但同 thread) ---")
    r2 = chat(agent, "alice", "你还记得我叫什么? 我做什么工作?")
    print(f"AI: {r2}")
    if "Alice" in r2 or "alice" in r2.lower():
        print("  ✅ Checkpointer 起作用 — Agent 记得 Alice")
    else:
        print("  ⚠️  Agent 似乎没记住 — 检查 thread_id 是否一致")

    # === 场景 2: bob 的会话 — thread_id 不同, 应该看不到 alice 的信息 ===
    print("\n--- thread_id='bob' 第 1 轮 (隔离) ---")
    r3 = chat(agent, "bob", "你好, 你认识 Alice 吗?")
    print(f"AI: {r3}")
    print("  (应该不认识 — bob 的会话和 alice 隔离)")

    # === 场景 3: 模拟程序重启 — 重新构造 agent (但 db 还在) ===
    print("\n--- 模拟程序重启 (重新构造 agent, db 不变) ---")
    conn.close()
    agent2, conn2 = build_agent_with_checkpointer()

    print("\n--- thread_id='alice' 第 3 轮 (跨重启) ---")
    r4 = chat(agent2, "alice", "我之前告诉你的工作是什么?")
    print(f"AI: {r4}")
    if "Java" in r4 or "java" in r4.lower():
        print("  ✅ 跨重启记忆 OK — DB 持久化生效")
    else:
        print("  ⚠️  跨重启没记住 — 检查 SqliteSaver 是否正确写盘")

    conn2.close()

    print("\n" + "=" * 60)
    print(f"DB 文件大小: {DB_PATH.stat().st_size} bytes")
    print(f"可以用 sqlite3 {DB_PATH} 看里面的表 (checkpoints / writes)")


if __name__ == "__main__":
    main()

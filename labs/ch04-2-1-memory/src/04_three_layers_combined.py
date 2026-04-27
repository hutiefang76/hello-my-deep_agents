"""04 · 三层记忆组合实战.

把短期 + 会话 + 长期记忆全部组合到一个 DeepAgent 上.

架构:
    +-------- 用户输入 --------+
                    |
    +-------- 长期检索 --------+   (从 InMemoryVectorStore 抽 top-3)
                    |
    +--- 注入 system_prompt ---+   (把检索结果塞 prompt)
                    |
    +-------- DeepAgent --------+
            |       |
    short-term      session
    (messages 窗口)  (SqliteSaver)
            |       |
    +-------- 工具调用 + 回复 --------+
                    |
    +-------- 写回长期 --------+   (重要事实写回 vector store)

Run:
    python 04_three_layers_combined.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402
from langgraph.checkpoint.sqlite import SqliteSaver  # noqa: E402


DB_PATH = Path(__file__).parent / "_three_layer.db"


def init_long_term_store() -> InMemoryVectorStore:
    """初始化长期记忆 — 预填几条事实."""
    embeddings = get_embeddings()
    vs = InMemoryVectorStore(embeddings)
    vs.add_documents(
        [
            Document(
                page_content="用户 Alice 是 Java 工程师, 团队主要用 Spring Boot",
                metadata={"user": "alice"},
            ),
            Document(
                page_content="Alice 提到团队没人懂 Python, 担心切换成本",
                metadata={"user": "alice"},
            ),
        ]
    )
    return vs


def build_agent_with_three_layers(checkpointer):
    """构造三层记忆的 Agent (短期靠 messages 窗口, 会话靠 checkpointer)."""
    return create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt=(
            "你是一个有长期记忆的研发顾问, 帮 Java 工程师转型 LLM 应用开发. "
            "如果用户说了重要事实 (如团队/技术栈), 请用 1 句话总结并提到 '我会记住'. "
            "回答简短, 100 字以内."
        ),
        checkpointer=checkpointer,
    )


def chat(agent, vector_store, user: str, thread_id: str, user_msg: str) -> str:
    """三层记忆对话:
    1. 长期检索 → 通过 messages 注入相关历史
    2. 会话: thread_id 让 checkpointer 自动续上 messages
    3. 短期: messages 窗口 (DeepAgents 内部管)
    """
    # 长期检索
    relevant = vector_store.similarity_search(user_msg, k=2)
    user_relevant = [d for d in relevant if d.metadata.get("user") == user][:2]

    # 把长期记忆塞进消息列表 (作为补充上下文)
    messages = []
    if user_relevant:
        memory_text = "; ".join(d.page_content for d in user_relevant)
        # 用 HumanMessage 模拟 "用户的过往背景"
        messages.append(
            HumanMessage(
                content=f"[系统提示: 用户 {user} 的过往背景: {memory_text}]"
            )
        )
    messages.append(HumanMessage(content=user_msg))

    result = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 10},
    )
    reply = result["messages"][-1].content

    # (可选) 把这次对话的关键事实回写长期库 — 教学简化, 这里 mock 一下
    if "我喜欢" in user_msg or "我们用" in user_msg or "我做" in user_msg:
        vector_store.add_documents(
            [
                Document(
                    page_content=f"{user} 在 {thread_id} 提到: {user_msg}",
                    metadata={"user": user, "thread": thread_id},
                )
            ]
        )

    return reply


def main() -> None:
    print("=" * 60)
    print("Ch4.2.1 · 04 三层记忆组合实战")
    print("=" * 60)

    if DB_PATH.exists():
        DB_PATH.unlink()

    vector_store = init_long_term_store()
    print(f"长期向量库初始化 OK ({len(vector_store.store)} 条历史)")

    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    agent = build_agent_with_three_layers(checkpointer)

    # === 模拟 Alice 的多轮对话 ===
    thread = "alice-2026-04-27"

    print("\n--- 第 1 轮: Alice 问技术建议 ---")
    r1 = chat(agent, vector_store, "alice", thread, "我们公司想引入 LLM, 但团队都是 Java, 你建议怎么办?")
    print(f"AI: {r1}")

    print("\n--- 第 2 轮: 同 thread, 跟进问题 ---")
    r2 = chat(agent, vector_store, "alice", thread, "如果不想全员学 Python, 还有别的选择吗?")
    print(f"AI: {r2}")

    print("\n--- 第 3 轮: Alice 透露偏好 ---")
    r3 = chat(agent, vector_store, "alice", thread, "我个人喜欢 Spring AI, 觉得它对 Java 友好.")
    print(f"AI: {r3}")
    print(f"  (写回长期库: vector_store 现在有 {len(vector_store.store)} 条)")

    print("\n--- 第 4 轮: 模拟程序重启, 用同 thread 续上 ---")
    conn.close()
    conn2 = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer2 = SqliteSaver(conn2)
    agent2 = build_agent_with_three_layers(checkpointer2)

    r4 = chat(agent2, vector_store, "alice", thread, "我刚才说我喜欢什么框架?")
    print(f"AI: {r4}")
    if "Spring AI" in r4 or "spring ai" in r4.lower():
        print("  ✅ 跨重启 + 长期记忆 OK")
    conn2.close()

    print("\n" + "=" * 60)
    print("观察:")
    print(f"  - 短期: messages 列表 (DeepAgent 内部窗口管理)")
    print(f"  - 会话: SqliteSaver 持久化到 {DB_PATH}")
    print(f"  - 长期: InMemoryVectorStore 含 {len(vector_store.store)} 条事实")
    print(f"  - 三层组合: 短期保证连贯, 会话保证不丢, 长期保证远期回忆")


if __name__ == "__main__":
    main()

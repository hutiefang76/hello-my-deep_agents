"""03 · 长期记忆 — 向量库语义检索过往对话.

会话记忆能跨 turn 续上, 但只能在同一 thread 内.
长期记忆把所有历史对话存到向量库, 新问题来时按语义相似度检索 — 实现"你上次说过 X" 的远期回忆.

本 lab 用 InMemoryVectorStore (langchain-core 内置, 不依赖外部数据库) +
DashScope text-embedding-v3 — 教学场景最稳.
真实项目用 pgvector / Milvus / Chroma.

教学要点:
    1. 用 DashScopeEmbeddings 做向量化
    2. InMemoryVectorStore 存 + 检索
    3. 在 LLM 调用前先检索相关历史, 塞进 system prompt

Run:
    python 03_long_term_vector.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402


def build_vector_store() -> InMemoryVectorStore:
    """构造向量库, 预填一批历史对话 (模拟用户过去聊过的话)."""
    embeddings = get_embeddings()
    vs = InMemoryVectorStore(embeddings)

    # 模拟过往对话片段 — 真实项目从历史 messages 抽取
    historical_facts = [
        Document(
            page_content="用户 Alice 是 Java 工程师, 工作 5 年, 现在想转 LLM 应用开发",
            metadata={"date": "2026-04-20", "user": "alice"},
        ),
        Document(
            page_content="Alice 喜欢用 Spring Boot, 觉得它 starter 自动装配很方便",
            metadata={"date": "2026-04-21", "user": "alice"},
        ),
        Document(
            page_content="Alice 最近在学 LangChain, 准备做一个内部知识库 RAG",
            metadata={"date": "2026-04-22", "user": "alice"},
        ),
        Document(
            page_content="Alice 提到团队没人懂 Python, 担心切换成本高",
            metadata={"date": "2026-04-23", "user": "alice"},
        ),
        Document(
            page_content="用户 Bob 是数据分析师, 主要用 Python pandas",
            metadata={"date": "2026-04-15", "user": "bob"},
        ),
        Document(
            page_content="Bob 想学 Agent 做自动化数据报告",
            metadata={"date": "2026-04-16", "user": "bob"},
        ),
    ]

    print(f"向量库初始化, 写入 {len(historical_facts)} 条历史对话...")
    vs.add_documents(historical_facts)
    return vs


def chat_with_long_term_memory(vs: InMemoryVectorStore, user: str, query: str) -> str:
    """带长期记忆的对话 — 先检索相关历史, 塞进 prompt."""
    # 1. 检索相关历史 (k 拉大, 然后用 metadata filter 过滤这个用户的)
    # 真实项目用 vector store 自带的 filter 参数, 这里教学场景拉大 k 后过滤
    relevant: list[Document] = vs.similarity_search(query, k=10)
    user_relevant = [d for d in relevant if d.metadata.get("user") == user][:3]

    print(f"  [检索] 命中 {len(user_relevant)} 条 {user} 的历史对话:")
    for d in user_relevant:
        print(f"    - [{d.metadata.get('date')}] {d.page_content}")

    # 2. 把检索结果塞进 system prompt
    if user_relevant:
        memory_block = "\n".join(
            f"- [{d.metadata.get('date')}] {d.page_content}" for d in user_relevant
        )
        system_msg = (
            f"你是一个有长期记忆的助手, 用户是 {user}. "
            f"以下是 {user} 过往告诉你的事 (按相关度排):\n\n"
            f"{memory_block}\n\n"
            f"基于这些信息回答, 100 字以内."
        )
    else:
        system_msg = f"你是一个助手. 用户 {user} 是新用户, 你不认识他."

    # 3. 调 LLM
    llm = get_llm()
    response = llm.invoke(
        [SystemMessage(content=system_msg), HumanMessage(content=query)]
    )
    return response.content


def main() -> None:
    print("=" * 60)
    print("Ch4.2.1 · 03 长期记忆 (向量检索过往对话)")
    print("=" * 60)

    vs = build_vector_store()

    print("\n--- 场景 1: Alice 问 '你了解我吗' ---")
    r1 = chat_with_long_term_memory(vs, "alice", "你了解我吗? 我做什么工作? 喜欢什么?")
    print(f"AI: {r1}")

    print("\n--- 场景 2: Alice 问 '我担心什么' (语义检索切到担忧那条) ---")
    r2 = chat_with_long_term_memory(vs, "alice", "我之前担心过什么问题?")
    print(f"AI: {r2}")

    print("\n--- 场景 3: Bob 问问题 (检索 bob 的, 不串台 alice) ---")
    r3 = chat_with_long_term_memory(vs, "bob", "我喜欢用什么编程语言? 最近想学什么?")
    print(f"AI: {r3}")

    print("\n--- 场景 4: Charlie 是新用户 (检索为空) ---")
    r4 = chat_with_long_term_memory(vs, "charlie", "你认识我吗?")
    print(f"AI: {r4}")

    print("\n" + "=" * 60)
    print("观察:")
    print("  - 向量检索按语义匹配, 不是关键词")
    print("  - 通过 metadata filter 实现用户隔离")
    print("  - 真实项目: 每次对话结束后, 把对话摘要塞回向量库 (持续更新)")


if __name__ == "__main__":
    main()

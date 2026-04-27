"""01 · LLM 调用基础 — invoke / stream / ainvoke 三种姿势.

教学要点:
    1. invoke()    — 同步, 一次性返回完整回复
    2. stream()    — 同步, 逐 token 返回 (流式)
    3. ainvoke()   — 异步, 适合并发场景

为什么直接用 ChatTongyi 不用 common/llm.py:
    第一节课要让学员看清"如何手动构造 LLM 实例", 知道每个参数的意思.
    后续 lab 全部用 common.llm.get_llm() 简化.

Run:
    python 01_chat_basic.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 加载仓库根目录的 .env
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from langchain_community.chat_models import ChatTongyi  # noqa: E402
from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402


def make_llm(streaming: bool = False) -> ChatTongyi:
    """构造一个 ChatTongyi 实例 — 这就是"原始姿势"."""
    return ChatTongyi(
        model=os.getenv("LLM_MODEL", "qwen-plus"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        streaming=streaming,
    )


def demo_invoke() -> None:
    """同步调用 — 等结果一次性返回."""
    print("--- 1. invoke (同步) ---")
    llm = make_llm()

    # 单条消息: 直接传字符串
    resp = llm.invoke("用一句话介绍 LangChain")
    print(f"单条字符串调用 → {resp.content[:80]}...")

    # 多条消息: 用 SystemMessage / HumanMessage 等结构化
    messages = [
        SystemMessage(content="你是一名 Java 高级工程师, 用 Java 工程师能听懂的话回答."),
        HumanMessage(content="一句话: LCEL 是什么?"),
    ]
    resp = llm.invoke(messages)
    print(f"多消息调用    → {resp.content[:80]}...")


def demo_stream() -> None:
    """流式调用 — 边出边显示, 不用等整段."""
    print("\n--- 2. stream (流式, 类似 ChatGPT 打字效果) ---")
    llm = make_llm(streaming=True)

    print("LLM > ", end="", flush=True)
    for chunk in llm.stream("用 30 字介绍 DeepAgents 框架"):
        print(chunk.content, end="", flush=True)
    print()


async def demo_ainvoke() -> None:
    """异步调用 + 并发 — LLM 应用必备."""
    print("\n--- 3. ainvoke (异步并发, 3 个问题同时问) ---")
    llm = make_llm()

    questions = [
        "1+1 等于几? 只回答数字",
        "2+2 等于几? 只回答数字",
        "3+3 等于几? 只回答数字",
    ]

    import time

    t0 = time.perf_counter()
    # asyncio.gather 同时发 3 个请求
    results = await asyncio.gather(*[llm.ainvoke(q) for q in questions])
    elapsed = time.perf_counter() - t0

    for q, r in zip(questions, results, strict=False):
        print(f"  Q: {q[:20]}...  A: {r.content.strip()}")
    print(f"  耗时: {elapsed:.2f}s (并发, 比串行 3x 快)")


def main() -> None:
    print("=" * 60)
    print("Ch2 · 01 LLM 调用基础")
    print("=" * 60)

    demo_invoke()
    demo_stream()
    asyncio.run(demo_ainvoke())

    print("\n--- 关键点 ---")
    print("  - invoke()  阻塞等完整结果, 适合脚本/测试")
    print("  - stream()  逐 token 返回, 适合 UI 展示打字效果")
    print("  - ainvoke() 异步, 配 asyncio.gather 实现并发")


if __name__ == "__main__":
    main()

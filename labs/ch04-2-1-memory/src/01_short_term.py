"""01 · 短期记忆 — messages 窗口截断.

最简单的记忆: 把过往消息塞进 messages 列表, 让 LLM 看到上下文.
问题: messages 越长 token 越多, 必须截断.

教学要点:
    1. ChatMessageHistory 管理 messages
    2. 窗口截断 (last N): 保留最近 N 条
    3. token-based 截断 (高级): 按 token 数算

Run:
    python 01_short_term.py
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
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402


WINDOW_SIZE = 4  # 只保留最近 4 轮 (8 条消息)


def chat_with_short_memory(messages: list, user_msg: str) -> tuple[str, list]:
    """带短期记忆的单次对话 — 返回 (LLM 回复, 更新后的 messages)."""
    llm = get_llm()

    # 加新消息
    messages.append(HumanMessage(content=user_msg))

    # 窗口截断: 保留 SystemMessage + 最近 WINDOW_SIZE 轮
    sys_msg = next((m for m in messages if isinstance(m, SystemMessage)), None)
    other = [m for m in messages if not isinstance(m, SystemMessage)]
    if len(other) > WINDOW_SIZE * 2:
        other = other[-WINDOW_SIZE * 2 :]  # 最近 N 轮 = 2N 条 (user + ai)

    truncated = ([sys_msg] if sys_msg else []) + other

    # 调 LLM
    response: AIMessage = llm.invoke(truncated)
    messages.append(response)

    return response.content, messages


def main() -> None:
    print("=" * 60)
    print("Ch4.2.1 · 01 短期记忆 (messages 窗口)")
    print("=" * 60)
    print(f"窗口大小: 最近 {WINDOW_SIZE} 轮对话")

    messages: list = [
        SystemMessage(content="你是一个简短回复的助手, 每次回答不超过 30 字."),
    ]

    # 模拟 6 轮对话, 第 5/6 轮看看 LLM 是否还记得第 1 轮的内容
    turns = [
        "我叫 Alice, 是一名 Java 工程师.",
        "我喜欢的颜色是蓝色.",
        "我最近在学 LangChain.",
        "我有一只猫叫 Tom.",
        "我们今天聊了几件事?",
        "我叫什么名字? 我喜欢什么颜色?",   # 测试 LLM 是否记得 (会被窗口截断)
    ]

    for i, q in enumerate(turns, 1):
        print(f"\n--- 第 {i} 轮 ---")
        print(f"User: {q}")
        reply, messages = chat_with_short_memory(messages, q)
        print(f"AI:   {reply}")
        print(f"  (当前 messages 长度: {len(messages)})")

    print("\n" + "=" * 60)
    print("观察:")
    print(f"  - 短期记忆只能保留最近 {WINDOW_SIZE} 轮")
    print(f"  - 第 6 轮提问 'Alice/蓝色' 时, 窗口已经把第 1/2 轮挤出去, LLM 可能不记得")
    print(f"  - 解决方案: 用会话 Checkpointer 持久化, 或长期向量记忆")


if __name__ == "__main__":
    main()

"""02 · L2 Single LLM Call — 单 LLM 客服.

特点:
    - 1 次 LLM 调用 (用长 system prompt 装入业务知识)
    - 处理口语化输入 (L1 处理不了的)
    - 不能查具体订单 (没工具)

升级理由 (Why upgrade from L1):
    用户说 "我那双鞋开胶了我急用" → L1 关键词不命中, L2 LLM 能理解 → 答退货政策

Run:
    python 02_l2_single_call.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from cs_kb import CS_KB  # noqa: E402


def l2_handle(query: str) -> dict:
    """L2 单 LLM — 把整个 KB 塞进 system prompt."""
    llm = get_llm()

    # 业务知识库塞进 system prompt
    kb_text = "\n".join(f"  - {k}: {v}" for k, v in CS_KB.items())

    system_prompt = (
        "你是电商客服. 严格基于以下 FAQ 回答, 不超出 80 字, 不编造信息.\n\n"
        f"FAQ:\n{kb_text}\n\n"
        "如果 FAQ 没覆盖, 说'建议联系人工客服'. 不要胡编."
    )

    t0 = time.perf_counter()
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ])
    elapsed = (time.perf_counter() - t0) * 1000

    return {
        "level": "L2",
        "answer": response.content,
        "ms": elapsed,
        "cost": 0.001,  # 估算
    }


def main() -> None:
    print("=" * 70)
    print("Ch9 · 02 L2 Single LLM Call — 单 LLM 客服")
    print("=" * 70)

    test_queries = [
        "我那双鞋开胶了, 急用!",                        # L1 不命中, L2 应答退货政策
        "怎么付钱?",                                    # 口语化, L1 也行
        "我刚成钻石啦, 有啥福利?",                      # L1 命中关键词"钻石", 但 L2 表达更自然
        "你们什么时候上班?",                            # 口语化, L1 关键词"上班"命中
        "我朋友要退货, 但他买的衣服已经穿过, 行吗?",      # 复杂条件判断, L2 能理解
    ]

    for query in test_queries:
        result = l2_handle(query)
        print(f"\n  Q: {query}")
        print(f"     A: {result['answer'][:120]}")
        print(f"     {result['ms']:.0f}ms, ~¥{result['cost']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - L2 能理解口语化 (L1 关键词搞不定)")
    print("  - 但 L2 把整个 KB 塞 prompt, KB 大了 token 爆炸")
    print("  - 仍不能查订单/退款 (没工具)")


if __name__ == "__main__":
    main()

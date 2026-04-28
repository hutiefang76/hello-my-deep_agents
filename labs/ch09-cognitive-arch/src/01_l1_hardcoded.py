"""01 · L1 Hardcoded — 硬编码 FAQ 客服.

特点 (Characteristics):
    - 0 LLM 调用, 0 cost, 0 ms latency
    - 关键词匹配 → KB 查表
    - 不能处理口语化/复杂表述

适用场景 (When to use):
    - 平台 70% 流量是 5-10 个标准 FAQ → 用 L1 兜底, 剩下 30% 才升级
    - 极致延迟需求 (<10ms)
    - 完全不想花 LLM 钱

Run:
    python 01_l1_hardcoded.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from cs_kb import CS_KB, KEYWORD_TO_FAQ  # noqa: E402


def l1_handle(query: str) -> dict:
    """L1 硬编码处理 — 关键词命中即答, 否则降级."""
    t0 = time.perf_counter()

    for keyword, faq_key in KEYWORD_TO_FAQ.items():
        if keyword in query:
            answer = CS_KB[faq_key]
            return {
                "level": "L1",
                "matched": True,
                "answer": answer,
                "ms": (time.perf_counter() - t0) * 1000,
                "cost": 0,
            }

    # 没命中 — 升级到 L2+
    return {
        "level": "L1",
        "matched": False,
        "answer": "[需升级到 L2+] 抱歉, FAQ 没有对应条目.",
        "ms": (time.perf_counter() - t0) * 1000,
        "cost": 0,
    }


def main() -> None:
    print("=" * 70)
    print("Ch9 · 01 L1 Hardcoded FAQ — 硬编码客服")
    print("=" * 70)

    test_queries = [
        ("退货怎么搞?", "应命中"),                          # 关键词"退货"
        ("我想问下支付方式", "应命中"),                      # 关键词"支付"
        ("钻石会员有什么权益?", "应命中"),                   # 关键词"钻石"
        ("我那双鞋开胶了, 烦死了", "应不命中 → 升级"),        # 口语化
        ("产品出问题了, 我要找你们闹一闹", "应不命中"),       # 投诉, L1 处理不了
        ("配送几天到?", "应命中"),
    ]

    matched = 0
    for query, expected in test_queries:
        result = l1_handle(query)
        emoji = "✅" if result["matched"] else "❌"
        if result["matched"]:
            matched += 1
        print(f"  {emoji} {query[:30]:<32} ({expected})")
        print(f"      → {result['answer'][:80]}")
        print(f"      → {result['ms']:.2f}ms, cost=¥{result['cost']}")

    print(f"\n  命中率: {matched}/{len(test_queries)} ({matched/len(test_queries)*100:.0f}%)")
    print()
    print("观察 (Observations):")
    print("  - 命中场景: 0ms, 0 成本 (L1 性价比天花板)")
    print("  - 不命中场景: 必须升级 L2+ (口语化/投诉/复杂表达)")
    print("  - 真实业务策略: L1 兜底 70% 流量, 节省 70% LLM 成本")


if __name__ == "__main__":
    main()

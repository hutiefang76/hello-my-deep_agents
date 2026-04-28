"""02 · Parallelization — 并行化 (Sectioning + Voting).

Anthropic Pattern #3.

两种变体 (Two Variations):
    1. Sectioning 章节分割: Break task into independent subtasks running in parallel.
                            把任务切成独立子任务并行跑.
    2. Voting     投票:     Run same task multiple times to get diverse outputs, vote.
                            同任务跑多次取多样输出, 投票决定.

何时用 (When):
    - 子任务独立无依赖 → Sectioning (大幅省时)
    - 需要多样性 / 减少幻觉 → Voting (多 LLM 投票降低单点错误)

双业务 (Dual Business):
    主 客服: 5 LLM 投票判断意图 (减少分类错误)
    对照 数分: 长报告章节并行写 (5 章并行 vs 顺序)

Run:
    python 02_parallelization.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from collections import Counter  # noqa: E402

from common.llm import get_llm  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnableParallel  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ============================================================
# Variation 1 · Voting (投票) — 客服意图分类
# ============================================================


class IntentVote(BaseModel):
    """单次 LLM 投票结果."""

    intent: Literal["faq", "order", "refund", "complaint", "chitchat"]
    confidence: float = Field(ge=0.0, le=1.0)


async def single_vote(message: str, vote_id: int) -> IntentVote:
    """单次投票: 用稍高 temperature 引入多样性."""
    llm = get_llm(temperature=0.7)  # 故意拉高让 voter 之间有多样性
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Classify intent: faq/order/refund/complaint/chitchat."),
            ("human", "{message}"),
        ]
    )
    chain = prompt | llm.with_structured_output(IntentVote)
    return await chain.ainvoke({"message": message})


async def voting_demo(message: str, num_voters: int = 5) -> dict:
    """5 个 LLM 同时投票, 多数胜."""
    print(f"  消息: {message}")
    print(f"  发起 {num_voters} 个并行投票...")

    t0 = time.perf_counter()
    votes = await asyncio.gather(*[single_vote(message, i) for i in range(num_voters)])
    elapsed = time.perf_counter() - t0

    intent_counts = Counter(v.intent for v in votes)
    winner, count = intent_counts.most_common(1)[0]
    avg_confidence = sum(v.confidence for v in votes) / len(votes)

    print(f"  各投票: {[v.intent for v in votes]}")
    print(f"  耗时: {elapsed:.2f}s (并发, 串行需 {elapsed * num_voters:.1f}s)")
    print(f"  胜出: {winner} ({count}/{num_voters} 票, 平均置信度 {avg_confidence:.2f})")

    return {
        "winner": winner,
        "count": count,
        "total": num_voters,
        "avg_confidence": avg_confidence,
        "elapsed_sec": round(elapsed, 2),
    }


# ============================================================
# Variation 2 · Sectioning (章节分割) — 数分长报告
# ============================================================


def sectioning_demo(topic: str) -> dict:
    """5 章并行写报告 vs 顺序写, 对比耗时."""
    llm = get_llm()
    parser = StrOutputParser()

    sections = [
        ("intro", "Introduction (引言, 50 字)"),
        ("background", "Background (背景, 80 字)"),
        ("analysis", "Analysis (核心分析, 150 字)"),
        ("trends", "Trends (趋势, 80 字)"),
        ("conclusion", "Conclusion (结论, 50 字)"),
    ]

    # ===== 方案 A: 顺序串行 =====
    print("  方案 A · 顺序写 5 章...")
    t0 = time.perf_counter()
    serial_results = {}
    for key, desc in sections:
        prompt = ChatPromptTemplate.from_template(
            f"Write the {desc} of a report on topic: {{topic}}. Markdown formatted."
        )
        serial_results[key] = (prompt | llm | parser).invoke({"topic": topic})
    serial_elapsed = time.perf_counter() - t0
    print(f"    顺序耗时: {serial_elapsed:.2f}s")

    # ===== 方案 B: 并行 (RunnableParallel) =====
    print("  方案 B · 并行写 5 章 (RunnableParallel)...")
    t0 = time.perf_counter()

    chains = {}
    for key, desc in sections:
        prompt = ChatPromptTemplate.from_template(
            f"Write the {desc} of a report on topic: {{topic}}. Markdown formatted."
        )
        chains[key] = prompt | llm | parser

    parallel = RunnableParallel(**chains)
    parallel_results = parallel.invoke({"topic": topic})
    parallel_elapsed = time.perf_counter() - t0
    print(f"    并行耗时: {parallel_elapsed:.2f}s")
    print(f"    加速比: {serial_elapsed / parallel_elapsed:.2f}x")

    return {
        "serial_sec": round(serial_elapsed, 2),
        "parallel_sec": round(parallel_elapsed, 2),
        "speedup": round(serial_elapsed / parallel_elapsed, 2),
        "section_count": len(sections),
        "report_preview": "\n\n".join(
            f"## {k}\n{v[:80]}..." for k, v in parallel_results.items()
        )[:400],
    }


def main() -> None:
    print("=" * 70)
    print("Ch6 · 02 Parallelization — Anthropic Pattern #3")
    print("=" * 70)

    print("\n--- Variation 1 [Voting 投票] · 主业务 客服意图分类 ---")
    asyncio.run(voting_demo("我那个洗了掉色的羽绒服快帮我退掉, 急用!", num_voters=5))

    print("\n--- Variation 2 [Sectioning 章节分割] · 对照 数分长报告 ---")
    result = sectioning_demo("LangChain vs LangGraph 选型分析")
    print(f"\n  报告片段:\n{result['report_preview']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - Voting 牺牲一点延迟 (并发) 换分类鲁棒性 — 多 LLM 投票防单点错误")
    print("  - Sectioning 显著降低长任务延迟 — 5 章并行近 5x 加速")
    print("  - 关键纪律: 子任务必须真独立 — 有依赖必须串行")
    print("=" * 70)


if __name__ == "__main__":
    main()

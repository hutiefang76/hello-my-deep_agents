"""03 · When Workflow Wins — Workflow 比 Agent 好的 3 个真实场景.

3 scenarios where Workflow is the right answer (反 Agent-everything 的迷思):
    1. Strict latency budget       严格延迟预算 (single-shot < 500ms)
    2. Compliance / Audit trail    合规/审计 (每步可解释 + 可重放)
    3. Cost-sensitive batch        成本敏感批处理 (百万级请求, 每分钱都算)

Each scenario includes a runnable Workflow vs Agent comparison.

Run:
    python 03_when_workflow_wins.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402


# ============================================================
# Scenario 1 · Strict Latency — 内容审核必须 <500ms
# ============================================================
def scenario_1_workflow(text: str) -> dict:
    """Workflow 实现: 单次 LLM + 严格 prompt + structured output."""
    from typing import Literal

    from pydantic import BaseModel, Field

    class Verdict(BaseModel):
        verdict: Literal["safe", "violation"] = Field(
            description="是否违规: safe=合规, violation=违规"
        )
        category: str = Field(description="违规分类, 合规填 'none'")

    llm = get_llm(temperature=0.0)
    structured = llm.with_structured_output(Verdict)
    t0 = time.perf_counter()
    result = structured.invoke(
        f"You are a content moderator. Classify the text below as 'safe' or 'violation'. "
        f"If safe, set category='none'. Reply with the schema only.\n\nText: {text}"
    )
    elapsed = (time.perf_counter() - t0) * 1000
    if result is None:
        return {"approach": "Workflow", "result": "(structured output returned None — fallback)",
                "ms": round(elapsed, 0)}
    return {"approach": "Workflow", "result": result.model_dump(), "ms": round(elapsed, 0)}


def scenario_1_agent(text: str) -> dict:
    """Agent 实现: 同任务用 DeepAgent (会有 planning/工具循环, 慢得多)."""
    agent = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt="You are a content moderator. Output 'safe' or 'violation' only.",
    )
    t0 = time.perf_counter()
    result = agent.invoke(
        {"messages": [HumanMessage(content=f"Moderate: {text}")]},
        config={"recursion_limit": 10},
    )
    elapsed = (time.perf_counter() - t0) * 1000
    msgs = result["messages"]
    return {
        "approach": "Agent",
        "result": msgs[-1].content[:60],
        "ms": round(elapsed, 0),
        "extra_messages": len(msgs),
    }


# ============================================================
# Scenario 2 · Compliance / Audit — 金融合规审批
# ============================================================
def scenario_2_workflow(loan_request: dict) -> dict:
    """Workflow 实现: 严格 4 步, 每步可审计."""
    audit_trail = []

    # Step 1: 信用分校验 (规则)
    t0 = time.perf_counter()
    if loan_request["credit_score"] < 600:
        audit_trail.append("Step 1: 信用分 < 600, 直接拒绝")
        return {
            "approach": "Workflow",
            "decision": "rejected",
            "audit_trail": audit_trail,
            "ms": round((time.perf_counter() - t0) * 1000, 0),
        }
    audit_trail.append(f"Step 1: 信用分 {loan_request['credit_score']} 通过")

    # Step 2: 收入比 (规则)
    debt_ratio = loan_request["amount"] / (loan_request["income"] * 12)
    if debt_ratio > 0.5:
        audit_trail.append(f"Step 2: 负债比 {debt_ratio:.2f} > 0.5, 拒绝")
        return {
            "approach": "Workflow",
            "decision": "rejected",
            "audit_trail": audit_trail,
            "ms": round((time.perf_counter() - t0) * 1000, 0),
        }
    audit_trail.append(f"Step 2: 负债比 {debt_ratio:.2f} 通过")

    # Step 3: LLM 风险描述生成 (固定 prompt, 不让 LLM 决策)
    llm = get_llm(temperature=0.0)
    risk_summary = llm.invoke(
        f"Summarize loan risk in 1 sentence (no decision making): {loan_request}"
    ).content
    audit_trail.append(f"Step 3: LLM 风险摘要: {risk_summary[:80]}")

    # Step 4: 规则决策 (不让 LLM 决策, 防 hallucination)
    audit_trail.append("Step 4: 通过规则审批")
    return {
        "approach": "Workflow",
        "decision": "approved",
        "audit_trail": audit_trail,
        "risk_summary": risk_summary,
        "ms": round((time.perf_counter() - t0) * 1000, 0),
    }


def scenario_2_agent(loan_request: dict) -> dict:
    """Agent 实现: LLM 自决 → 不可解释 + 可能 hallucinate 决策."""
    llm = get_llm()
    t0 = time.perf_counter()
    response = llm.invoke(
        f"You are a loan officer. Decide approve/reject for: {loan_request}. "
        f"Reply: 'approved' or 'rejected' with reason."
    ).content
    return {
        "approach": "Agent",
        "decision_text": response[:200],
        "ms": round((time.perf_counter() - t0) * 1000, 0),
        "audit_trail": ["Single LLM call, no step-by-step trace"],
    }


# ============================================================
# Scenario 3 · Cost-Sensitive Batch — 千次商品分类
# ============================================================
def scenario_3_workflow(products: list[str]) -> dict:
    """Workflow 实现: 单次 LLM, 一个 prompt 处理所有 (batch)."""
    llm = get_llm(temperature=0.0)
    parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_template(
        "Classify each product into one of: electronics/clothing/food/other. "
        "Reply ONE line per product, format 'i. category'.\n\nProducts:\n{items}"
    )
    chain = prompt | llm | parser

    t0 = time.perf_counter()
    items = "\n".join(f"{i}. {p}" for i, p in enumerate(products, 1))
    result = chain.invoke({"items": items})
    elapsed = (time.perf_counter() - t0) * 1000

    # 1 次 LLM call 处理 N 商品 → cost ≈ 1x
    return {
        "approach": "Workflow (batch)",
        "result_preview": result[:200],
        "ms": round(elapsed, 0),
        "llm_calls": 1,
        "cost_unit": "1x",
    }


def scenario_3_agent(products: list[str]) -> dict:
    """Agent 实现: 每商品独立 invoke (Agent 想"思考思考")."""
    agent = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt="Classify product into electronics/clothing/food/other. One word.",
    )

    t0 = time.perf_counter()
    results = []
    for p in products:
        out = agent.invoke(
            {"messages": [HumanMessage(content=f"Classify: {p}")]},
            config={"recursion_limit": 5},
        )
        results.append(out["messages"][-1].content[:30])
    elapsed = (time.perf_counter() - t0) * 1000

    # N 次 LLM call → cost ≈ Nx
    return {
        "approach": "Agent (per-item)",
        "result_preview": " | ".join(results),
        "ms": round(elapsed, 0),
        "llm_calls": len(products),
        "cost_unit": f"{len(products)}x",
    }


def main() -> None:
    print("=" * 70)
    print("Ch5 · 03 When Workflow Wins — Workflow 何时更优 (反 Agent-everything)")
    print("=" * 70)

    # ===== Scenario 1 =====
    print("\n[Scenario 1] Content Moderation 内容审核 (严格延迟 <500ms)")
    text = "I love programming with Python."
    w = scenario_1_workflow(text)
    a = scenario_1_agent(text)
    print(f"  Workflow: {w['ms']:>6}ms · {w['result']}")
    print(f"  Agent:    {a['ms']:>6}ms · {a['result']}  (extra_messages={a.get('extra_messages')})")
    print(f"  → 延迟比: Agent 慢 {a['ms'] / max(w['ms'], 1):.1f}x")

    # ===== Scenario 2 =====
    print("\n[Scenario 2] Loan Approval 贷款审批 (合规 + 审计追溯)")
    loan = {"credit_score": 720, "income": 8000, "amount": 30000, "purpose": "renovation"}
    w = scenario_2_workflow(loan)
    a = scenario_2_agent(loan)
    print(f"  Workflow: decision={w['decision']}, audit_trail={len(w['audit_trail'])} steps")
    for step in w["audit_trail"]:
        print(f"    - {step[:80]}")
    print(f"  Agent:    {a['decision_text'][:80]}")
    print(f"    audit_trail: {a['audit_trail']}")
    print(f"  → 审计可追溯性: Workflow {len(w['audit_trail'])} steps · Agent 1 step (黑盒)")

    # ===== Scenario 3 =====
    print("\n[Scenario 3] Product Classification 商品批量分类 (5 商品, 真实业务可能千万级)")
    products = [
        "iPhone 16 Pro Max",
        "Levi's 501 jeans",
        "Coca-Cola 330ml",
        "Sony WH-1000XM6",
        "Organic apples 5kg",
    ]
    w = scenario_3_workflow(products)
    a = scenario_3_agent(products)
    print(f"  Workflow (batch): {w['llm_calls']:>2} LLM call,  cost={w['cost_unit']:<5}, {w['ms']}ms")
    print(f"  Agent (per-item): {a['llm_calls']:>2} LLM calls, cost={a['cost_unit']:<5}, {a['ms']}ms")
    print(f"  → 成本比: Agent 比 Workflow 贵 {len(products)}x")
    print(f"  → 千万级商品时, Workflow 省 ${(len(products) - 1) * 0.001 * 10_000_000 / 1000:.0f}K (假设单 call $0.001)")

    # ===== 总结 =====
    print("\n" + "=" * 70)
    print("Anthropic 原文 (English):")
    print('  "Don\'t use complex frameworks unless your task fundamentally needs them."')
    print("中文:")
    print("  '不要用复杂框架，除非你的任务本质上需要.'")
    print()
    print("3 个 Workflow 胜出场景 (3 wins for Workflow):")
    print("  1. Strict latency  严格延迟 (real-time, <500ms)")
    print("  2. Compliance      合规审计 (每步可解释/可重放)")
    print("  3. Batch cost      批量成本 (百万级请求每分钱都算)")
    print("=" * 70)


if __name__ == "__main__":
    main()

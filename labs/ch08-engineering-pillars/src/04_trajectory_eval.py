"""04 · Trajectory Evaluation — 轨迹评估 (而非终态评估).

OpenAI Guide: "Evaluate full trajectories, not just the final message:
tool choice correctness, argument validity, step count, time/cost, policy compliance."

Trajectory vs Final-State (轨迹 vs 终态):
    Final-state eval: 只看最终输出对不对
    Trajectory eval:  看整个执行链路 (步数/工具选/参数对/合规)
                      → 能发现"答对了但绕远路"的问题

7 Span Types (LangSmith / OpenTelemetry 标准):
    CHAIN / RETRIEVER / RERANKER / LLM / EMBEDDING / TOOL / AGENT

Run:
    python 04_trajectory_eval.py
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langgraph.prebuilt import create_react_agent  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ============================================================
# 简化 Tracer (模拟 LangSmith)
# ============================================================


@dataclass
class Span:
    """7 span types of OpenTelemetry."""

    span_type: str  # CHAIN / RETRIEVER / RERANKER / LLM / EMBEDDING / TOOL / AGENT
    name: str
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


@dataclass
class Trajectory:
    """完整轨迹."""

    spans: list[Span] = field(default_factory=list)

    def add(self, span: Span):
        self.spans.append(span)

    def total_ms(self) -> float:
        return sum(s.duration_ms for s in self.spans)

    def tool_calls(self) -> list[Span]:
        return [s for s in self.spans if s.span_type == "TOOL"]

    def llm_calls(self) -> list[Span]:
        return [s for s in self.spans if s.span_type == "LLM"]


# ============================================================
# Mock Agent + Trajectory 收集
# ============================================================


@tool
def query_order(order_id: str) -> str:
    """查询订单状态.

    Args:
        order_id: 订单 ID
    """
    return f"Order {order_id}: shipped, ETA tomorrow"


@tool
def issue_refund(order_id: str, amount: float) -> str:
    """发起退款.

    Args:
        order_id: 订单 ID
        amount: 金额
    """
    return f"Refund issued for {order_id}: {amount}"


def run_with_trajectory(query: str, expected_tools: list[str]) -> tuple[str, Trajectory]:
    """跑一个 Agent 并收集 trajectory."""
    traj = Trajectory()

    # 顶层 CHAIN span
    t0 = time.perf_counter()
    traj.add(Span(span_type="CHAIN", name="customer_service_agent", duration_ms=0))

    agent = create_react_agent(
        model=get_llm(),
        tools=[query_order, issue_refund],
        prompt="你是客服, 必要时调工具, 给简洁答复.",
    )
    result = agent.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"recursion_limit": 10},
    )

    # 收集每个 LLM/TOOL span (简化: 从 result messages 反推)
    for m in result["messages"]:
        if isinstance(m, ToolMessage):
            traj.add(
                Span(
                    span_type="TOOL",
                    name=m.name if hasattr(m, "name") else "unknown_tool",
                    duration_ms=10.0,  # mock
                    metadata={"output_preview": m.content[:80]},
                )
            )
        elif hasattr(m, "tool_calls") and m.tool_calls:
            traj.add(
                Span(
                    span_type="LLM",
                    name="planner_llm",
                    duration_ms=500.0,  # mock
                    metadata={"tool_calls": [tc["name"] for tc in m.tool_calls]},
                )
            )
        elif hasattr(m, "content") and not isinstance(m, HumanMessage):
            traj.add(Span(span_type="LLM", name="responder_llm", duration_ms=300.0))

    traj.spans[0].duration_ms = (time.perf_counter() - t0) * 1000
    return result["messages"][-1].content, traj


# ============================================================
# Trajectory Evaluator (轨迹评估器)
# ============================================================


class TrajectoryScore(BaseModel):
    """4 维评分."""

    tool_choice_correct: bool = Field(description="工具选择是否正确")
    args_valid: bool = Field(description="参数是否有效")
    step_count_reasonable: bool = Field(description="步数是否合理 (不绕远路)")
    policy_compliant: bool = Field(description="是否合规 (无敏感词/越权)")
    overall_score: int = Field(ge=0, le=100)
    issues: list[str] = Field(default_factory=list)


def evaluate_trajectory(
    query: str, traj: Trajectory, final: str, expected_tools: list[str]
) -> TrajectoryScore:
    """LLM-as-judge 评估轨迹."""
    tool_calls = [s.name for s in traj.tool_calls()]
    llm_calls_count = len(traj.llm_calls())

    judge = get_llm(temperature=0.0)
    prompt = (
        f"Evaluate this Agent trajectory:\n\n"
        f"Query: {query}\n"
        f"Tools called: {tool_calls}\n"
        f"Expected tools: {expected_tools}\n"
        f"LLM calls count: {llm_calls_count}\n"
        f"Total duration: {traj.total_ms():.0f}ms\n"
        f"Final answer: {final}\n\n"
        f"Score on 4 dimensions: tool_choice / args / step_count / policy_compliance.\n"
        f"Be strict — average should be 70."
    )
    return judge.with_structured_output(TrajectoryScore).invoke(prompt)


def main() -> None:
    print("=" * 70)
    print("Ch8 · 04 Trajectory Evaluation (轨迹评估)")
    print("=" * 70)

    test_cases = [
        {
            "query": "查订单 O20260428 状态",
            "expected_tools": ["query_order"],
        },
        {
            "query": "订单 O20260427 鞋子开胶, 退款 599",
            "expected_tools": ["issue_refund"],
        },
        {
            "query": "查订单 O123 的状态, 然后退款 100 元",
            "expected_tools": ["query_order", "issue_refund"],
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Case {i}: {case['query']} ---")
        final, traj = run_with_trajectory(case["query"], case["expected_tools"])
        print(f"  Trajectory ({len(traj.spans)} spans):")
        for s in traj.spans:
            meta_str = f" {s.metadata}" if s.metadata else ""
            print(f"    [{s.span_type:<10}] {s.name} {s.duration_ms:.0f}ms{str(meta_str)[:80]}")
        print(f"  Final: {final[:100]}")

        # 评估
        score = evaluate_trajectory(
            case["query"], traj, final, case["expected_tools"]
        )
        print(f"\n  📊 Trajectory Score:")
        print(f"     tool_choice={score.tool_choice_correct}, "
              f"args={score.args_valid}, "
              f"steps={score.step_count_reasonable}, "
              f"policy={score.policy_compliant}")
        print(f"     overall={score.overall_score}/100")
        if score.issues:
            print(f"     issues: {score.issues}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 终态评估只看 final, 看不到'对的答案+错的工具'")
    print("  - 轨迹评估能发现: 多调一次工具浪费 / 调错工具撞对结果")
    print("  - 7 Span Types 是 LangSmith / OpenTelemetry 行业标准")
    print()
    print("OpenAI 原文: 'Evaluate full trajectories, not just the final message.'")
    print("=" * 70)


if __name__ == "__main__":
    main()

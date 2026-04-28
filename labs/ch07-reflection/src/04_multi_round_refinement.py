"""04 · Multi-Round Refinement — 多轮精炼 + 质量阈值.

Andrew Ng Reflection Pattern (Variant 4): 设质量分阈值, 多轮直到达标.

教学要点:
    1. 量化质量分 (LLM-as-judge 给 0-100 分)
    2. 设阈值 (比如 80)
    3. 不达标 → 反馈 + 重生成
    4. 跟踪质量分轨迹 (看是否真的在提升)

成本-收益曲线 (Cost-Benefit Curve):
    Round 1 → 60 分     (基础)
    Round 2 → 78 分     (+18, 性价比高)
    Round 3 → 85 分     (+7, 边际递减)
    Round 4 → 88 分     (+3, 已经不值得)
    → 拐点通常在 round 2-3, 之后边际成本 > 收益

Run:
    python 04_multi_round_refinement.py
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
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


class QualityScore(BaseModel):
    """LLM-as-judge 评分."""

    score: int = Field(ge=0, le=100, description="质量分 0-100")
    breakdown: dict = Field(
        description="维度细分分数, e.g. {'accuracy': 80, 'clarity': 70, 'depth': 90}"
    )
    weak_points: list[str] = Field(description="3 个最弱的具体点")
    suggestions: list[str] = Field(description="3 个改进建议")


def llm_as_judge(task: str, output: str, criteria: list[str]) -> QualityScore:
    """LLM 当评委给质量分."""
    llm = get_llm(temperature=0.0)
    crit_str = "\n".join(f"  - {c}" for c in criteria)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a strict quality judge. Score the output 0-100 on the criteria.\n"
                f"Criteria:\n{crit_str}\n\n"
                "Be harsh — average should be 60. Reserve 90+ for truly excellent.",
            ),
            ("human", "Task: {task}\n\nOutput to judge:\n{output}"),
        ]
    )
    return (prompt | llm.with_structured_output(QualityScore)).invoke(
        {"task": task, "output": output}
    )


def multi_round_refinement(
    task: str,
    role: str,
    criteria: list[str],
    threshold: int = 80,
    max_rounds: int = 5,
) -> dict:
    """多轮精炼直到 score ≥ threshold."""
    llm = get_llm()

    gen_prompt = ChatPromptTemplate.from_template(
        "{role}\n\nTask: {task}\n\nPrevious feedback: {feedback}"
    )

    feedback = "(no feedback yet, first attempt)"
    score_trajectory = []
    history = []

    for r in range(1, max_rounds + 1):
        print(f"\n  [Round {r}]")
        # Generate
        output = (gen_prompt | llm | StrOutputParser()).invoke(
            {"role": role, "task": task, "feedback": feedback}
        )

        # Judge
        try:
            quality = llm_as_judge(task, output, criteria)
        except Exception as e:
            print(f"  [Judge ERROR] {e}, 跳过本轮评分")
            history.append({"round": r, "output": output, "score": None})
            break

        score_trajectory.append(quality.score)
        print(f"  [Output] {output[:80]}...")
        print(f"  [Judge]  score={quality.score}/100, breakdown={quality.breakdown}")
        print(f"           weak_points={quality.weak_points}")

        history.append(
            {
                "round": r,
                "output": output,
                "score": quality.score,
                "breakdown": quality.breakdown,
                "weak_points": quality.weak_points,
            }
        )

        if quality.score >= threshold:
            print(f"  ✅ Round {r} 达到阈值 {threshold}, 退出")
            return {
                "final": output,
                "final_score": quality.score,
                "rounds": r,
                "trajectory": score_trajectory,
                "history": history,
            }

        # 把 weak points + suggestions 塞下一轮
        feedback = (
            f"Score {quality.score}/{threshold}. Weak: {quality.weak_points}. "
            f"Suggestions: {quality.suggestions}"
        )

    return {
        "final": history[-1]["output"],
        "final_score": history[-1]["score"],
        "rounds": max_rounds,
        "trajectory": score_trajectory,
        "history": history,
        "max_rounds_hit": True,
    }


def main() -> None:
    print("=" * 70)
    print("Ch7 · 04 Multi-Round Refinement — 多轮精炼 + 质量阈值")
    print("=" * 70)

    # ===== 主业务: 客服回复 =====
    print("\n--- [主业务] 客服回复多轮精炼 ---")
    cs_role = "你是电商客服, 回复客户投诉. 80 字以内中文."
    cs_task = "客户投诉: 鞋子开胶 + 退货流程很慢, 我已经等了一周!"
    cs_criteria = [
        "Empathy (共情度)",
        "Action clarity (行动清晰度: 给出明确下一步)",
        "Compliance (无敏感承诺词: 保证/绝对/100%)",
        "Conciseness (简洁: 不超过 80 字)",
    ]
    cs_result = multi_round_refinement(
        cs_task, cs_role, cs_criteria, threshold=85, max_rounds=4
    )
    print(
        f"\n  Score 轨迹: {cs_result['trajectory']}  "
        f"→ 最终 {cs_result['final_score']}/100"
    )

    # ===== 对照业务: 数分洞察 =====
    print("\n\n--- [对照业务] 数据分析洞察多轮精炼 ---")
    da_role = "你是数据分析师, 写销售简报给 CEO."
    da_task = (
        "数据: 上周销售 1500 单 (+25% YoY); 退货率 12% (前 6%); "
        "客单价 ¥320 (-5%); 投诉率 3.2% (前 1.5%). 给 CEO 100 字内简报."
    )
    da_criteria = [
        "Data accuracy (数字准确, 不胡编)",
        "Insight depth (有具体洞察, 不空洞)",
        "Actionable recommendation (含可执行建议)",
        "Brevity (≤ 100 字)",
    ]
    da_result = multi_round_refinement(
        da_task, da_role, da_criteria, threshold=85, max_rounds=4
    )
    print(
        f"\n  Score 轨迹: {da_result['trajectory']}  "
        f"→ 最终 {da_result['final_score']}/100"
    )

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 质量分轨迹通常: 60 → 78 → 85 (拐点在 round 2-3)")
    print("  - 边际收益递减: round 4-5 的提升通常不值得多花的成本")
    print("  - 实战阈值: 80-85 (再高的成本爆炸, 再低的质量不够)")
    print("  - LLM-as-judge 自带偏见, 用 temperature=0 + 严苛 system prompt 缓解")
    print("=" * 70)


if __name__ == "__main__":
    main()

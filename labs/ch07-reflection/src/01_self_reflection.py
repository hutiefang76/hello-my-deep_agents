"""01 · Self-Reflection — 单 Agent 自评自改.

Andrew Ng Reflection Pattern (Variant 1): 同一个 LLM 实例先生成, 再用批评性 prompt
让自己评估自己, 然后改进.

vs Ch6/03 Evaluator-Optimizer:
    - 那里是 *两个不同 prompt 的 LLM 角色* (workflow)
    - 这里是 *同一 LLM* 多轮自我反思 (agent self-improvement)

教学要点:
    1. 第一次调用: 直接生成 (initial draft 初稿)
    2. 第二次调用: 给 LLM 看自己的初稿 + 批评性 prompt
    3. 第三次调用: 综合反思改进

双业务 (Dual Business):
    主 客服: 回复初稿 (可能太强硬) → 自审 → 改 (共情)
    对照 数分: 数据洞察初稿 → 自审 (准确性/可读性) → 改

Run:
    python 01_self_reflection.py
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


def self_reflection(task: str, system_role: str, max_rounds: int = 2) -> dict:
    """通用 Self-Reflection 模板.

    Returns:
        {"draft": ..., "critiques": [...], "final": ..., "rounds": N}
    """
    llm = get_llm()

    # ===== Round 0: Initial Draft =====
    print(f"\n  [Round 0] Initial draft")
    messages = [
        SystemMessage(content=system_role),
        HumanMessage(content=task),
    ]
    draft: AIMessage = llm.invoke(messages)
    print(f"  → 初稿: {draft.content[:100]}...")

    history = {"draft": draft.content, "critiques": [], "improvements": []}

    current = draft.content

    for r in range(1, max_rounds + 1):
        # ===== Self-Critique =====
        print(f"\n  [Round {r}] Self-Critique (LLM 批自己)")
        critique_msgs = [
            SystemMessage(content=system_role),
            HumanMessage(content=task),
            AIMessage(content=current),
            HumanMessage(
                content=(
                    "Now, critically review your own response above. "
                    "List 3 specific weaknesses (语气/准确性/可读性/完整性). "
                    "Be brutally honest — don't sugarcoat. "
                    "Format: '1. weakness 1\\n2. weakness 2\\n3. weakness 3'"
                )
            ),
        ]
        critique = llm.invoke(critique_msgs)
        print(f"  → 自评: {critique.content[:150]}...")
        history["critiques"].append(critique.content)

        # ===== Self-Improvement =====
        print(f"  [Round {r}] Self-Improvement (LLM 改自己)")
        improve_msgs = critique_msgs + [
            critique,
            HumanMessage(
                content=(
                    "Based on your own critique above, rewrite your response addressing "
                    "all 3 weaknesses. Output the improved version only."
                )
            ),
        ]
        improved = llm.invoke(improve_msgs)
        print(f"  → 改进版: {improved.content[:100]}...")
        history["improvements"].append(improved.content)

        current = improved.content  # 下一轮基于这个继续

    history["final"] = current
    history["rounds"] = max_rounds
    return history


def main() -> None:
    print("=" * 70)
    print("Ch7 · 01 Self-Reflection — 单 Agent 自评自改 (Andrew Ng Pattern)")
    print("=" * 70)

    # ===== 主业务: 客服回复 =====
    print("\n--- [主业务] 客服回复初稿 → 自审 → 改 ---")
    cs_role = "你是电商客服, 回复客户投诉. 简洁 ≤ 80 字."
    cs_task = "客户投诉: 我买的鞋子穿一次就开胶, 非常生气, 要求 100% 全额退款 + 双倍赔偿!"
    cs_result = self_reflection(cs_task, cs_role, max_rounds=2)

    print("\n  --- 改进对比 ---")
    print(f"  初稿:    {cs_result['draft'][:120]}")
    print(f"  最终:    {cs_result['final'][:120]}")

    # ===== 对照业务: 数据分析报告 =====
    print("\n\n--- [对照业务] 数据分析洞察初稿 → 自审 → 改 ---")
    da_role = "你是数据分析师, 写销售洞察简报. 简洁 ≤ 100 字, 含 1 个具体建议."
    da_task = (
        "数据: 上周销售 1500 单, 同比 +25%; 但退货率 12% (上周 6%); "
        "客单价 ¥320 (-5%). 写一段管理层简报."
    )
    da_result = self_reflection(da_task, da_role, max_rounds=2)

    print("\n  --- 改进对比 ---")
    print(f"  初稿:    {da_result['draft'][:120]}")
    print(f"  最终:    {da_result['final'][:120]}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 同一 LLM 给批评性 prompt 后, 能识别自己的问题 (惊人但真实)")
    print("  - 改进版通常更有结构 / 更具体 / 语气更平衡")
    print("  - 成本: 1 task 约 5 次 LLM (初稿+2 轮 critique+improve)")
    print("  - Andrew Ng: 'Reflection alone gave bigger gains than model upgrade.'")
    print("=" * 70)


if __name__ == "__main__":
    main()

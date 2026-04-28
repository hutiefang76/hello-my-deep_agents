"""01 · Decision Tree — Workflow or Agent? (决策树)

Based on Anthropic's "Building Effective Agents" (2024-12).

5 real tasks, classify each: Workflow / Agent / Hybrid.

教学要点 (Teaching Points):
    1. 不是所有 LLM 应用都该是 Agent (Not every LLM app should be an Agent)
    2. 用 LLM 判断 + 给出推理 (LLM-based classifier with reasoning)
    3. 决策维度 (Decision Dimensions):
       - Determinism 确定性
       - Autonomy 自主性
       - Cost 成本
       - Observability 可观测性

Run:
    python 01_decision_tree.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


class Decision(BaseModel):
    """Workflow vs Agent decision (基于 Anthropic mental model)."""

    recommendation: Literal["workflow", "agent", "hybrid"] = Field(
        description="workflow=固定流程, agent=LLM自决, hybrid=外层workflow内层agent"
    )
    determinism_score: int = Field(ge=1, le=10, description="任务确定性 1-10 (10=高度确定)")
    autonomy_needed: int = Field(ge=1, le=10, description="需要的自主性 1-10 (10=完全自主)")
    cost_sensitivity: int = Field(ge=1, le=10, description="成本敏感度 1-10 (10=极敏感)")
    reasoning: str = Field(description="一句话推理 (one-sentence reasoning)")
    risks_if_use_agent: str = Field(description="若选 agent 的风险 (risks if choosing agent)")


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an LLM application architect (LLM 应用架构师), follow Anthropic's "
            "'Building Effective Agents' mental model.\n\n"
            "Definition (定义):\n"
            "- Workflow (工作流): LLMs orchestrated through PREDEFINED code paths. "
            "  LLMs orchestrated through predefined code paths.\n"
            "- Agent (智能体): LLMs DYNAMICALLY direct their own processes and tool usage.\n"
            "- Hybrid (混合): outer workflow + inner agent for sub-tasks.\n\n"
            "Decision criteria (决策标准):\n"
            "  1. Steps fixed? (步骤固定?) → workflow\n"
            "  2. LLM decides next? (LLM 决策下一步?) → agent\n"
            "  3. High cost of error (e.g. finance, medical)? → workflow + guardrails\n"
            "  4. Creative / open-ended? → agent\n"
            "  5. Strict cost budget? → workflow (cheaper)\n"
            "  6. Real-time single-shot? → workflow\n\n"
            "Output strict Pydantic schema."
        ),
        ("human", "Task description (任务描述):\n{task}"),
    ]
)


def decide(task: str) -> Decision:
    llm = get_llm(temperature=0.0)
    chain = _PROMPT | llm.with_structured_output(Decision)
    return chain.invoke({"task": task})


def main() -> None:
    print("=" * 70)
    print("Ch5 · 01 Decision Tree — Workflow or Agent?")
    print("(基于 Anthropic Building Effective Agents)")
    print("=" * 70)

    tasks = [
        # (任务名 task name, 任务描述 description)
        (
            "FAQ Customer Bot 客服 FAQ 机器人",
            "用户问退货政策/支付方式/营业时间, 知识库里全有, 直接检索回答即可.",
        ),
        (
            "Content Moderation 内容审核",
            "用户上传文本, 判断是否违反 5 条社区规则 (色情/暴力/政治/广告/隐私), "
            "输出违规分类 + 置信度. 错判代价高 (法律风险).",
        ),
        (
            "Research Assistant 研究助手",
            "用户给一个开放问题 'LangChain vs LangGraph 该用哪个?', "
            "Agent 需要联网搜资料 + 综合分析 + 出 markdown 研究报告. "
            "步骤数量不固定, 可能 3 步可能 8 步.",
        ),
        (
            "Code Reviewer 代码审查",
            "GitHub PR 提交时, LLM 看 diff, 找 3 个潜在问题 (bug / 性能 / 风格), "
            "输出 JSON 评论列表. 单次调用, 无需多步.",
        ),
        (
            "Data Analyst 数据分析师",
            "用户给一个 .csv 文件 + 问题 '哪个产品销量最好?', "
            "Agent 需要: 读文件 → 写 pandas 代码 → 跑代码 → 看结果 → 可能改代码再跑 → 出可视化. "
            "步骤数取决于数据复杂度.",
        ),
    ]

    for name, desc in tasks:
        print(f"\n--- 任务: {name} ---")
        print(f"描述: {desc[:80]}...")

        decision = decide(desc)

        rec_zh = {"workflow": "工作流", "agent": "智能体", "hybrid": "混合"}[
            decision.recommendation
        ]
        emoji = {"workflow": "⚙️ ", "agent": "🤖", "hybrid": "🔀"}[decision.recommendation]

        print(f"  {emoji} 推荐: {decision.recommendation} ({rec_zh})")
        print(
            f"  Determinism={decision.determinism_score}/10, "
            f"Autonomy={decision.autonomy_needed}/10, "
            f"Cost-Sensitive={decision.cost_sensitivity}/10"
        )
        print(f"  Reasoning: {decision.reasoning}")
        print(f"  Risks: {decision.risks_if_use_agent}")

    print("\n" + "=" * 70)
    print("关键洞察 (Key Insight):")
    print("  - 高确定性 + 低自主性 + 高成本敏感 = Workflow")
    print("  - 低确定性 + 高自主性 + 创造性 = Agent")
    print("  - 错判代价高 (compliance) = Workflow + Guardrails")
    print("=" * 70)


if __name__ == "__main__":
    main()

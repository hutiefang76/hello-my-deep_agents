"""04 · Pattern Compare — 5 模式对照决策表.

不写新 demo, 而是把 5 模式总结+决策表呈现给学员.
覆盖:
    1. Prompt Chaining     (本章 01)
    2. Routing             (Ch4.2.2 已实现)
    3. Parallelization     (本章 02)
    4. Orchestrator-Workers (Ch4.2.4 SubAgent 已实现)
    5. Evaluator-Optimizer (本章 03)

Run:
    python 04_pattern_compare.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None


PATTERNS = [
    {
        "name": "Prompt Chaining",
        "中文": "提示词串联",
        "结构": "step1 → gate → step2 → gate → step3",
        "何时用": "任务可线性拆 + 中间需校验",
        "本仓库": "Ch6/01_prompt_chaining.py (本章新增)",
        "成本": "中 (N 次 LLM 顺序)",
        "可控性": "高",
    },
    {
        "name": "Routing",
        "中文": "路由",
        "结构": "classify → branch_A | branch_B | ...",
        "何时用": "输入需分流到不同 handler (客服分意图)",
        "本仓库": "Ch4.2.2 (已实现)",
        "成本": "低 (1 次 LLM 分类 + 1 次 handler)",
        "可控性": "高",
    },
    {
        "name": "Parallelization",
        "中文": "并行化",
        "结构": "task → [worker_1 | worker_2 | ...] → aggregate",
        "何时用": "子任务独立 (Sectioning) / 多次投票 (Voting)",
        "本仓库": "Ch6/02_parallelization.py (本章新增)",
        "成本": "中 (N 个 LLM 并发, 但耗时 ≈ 1)",
        "可控性": "中",
    },
    {
        "name": "Orchestrator-Workers",
        "中文": "主管-工人",
        "结构": "manager_LLM → dynamic [worker_1 ... worker_N] → manager 综合",
        "何时用": "任务结构动态 (manager 决定切几块)",
        "本仓库": "Ch4.2.4 SubAgent (已实现)",
        "成本": "高 (Manager 反复决策 + N workers)",
        "可控性": "中",
    },
    {
        "name": "Evaluator-Optimizer",
        "中文": "评估-优化循环",
        "结构": "generate → evaluate → (pass? END : retry with feedback)",
        "何时用": "评估标准清晰 + 迭代精炼有价值",
        "本仓库": "Ch6/03_evaluator_optimizer.py (本章新增)",
        "成本": "高 (1-N 轮 generator + evaluator)",
        "可控性": "高 (max_rounds 兜底)",
    },
]


def print_table() -> None:
    print("=" * 90)
    print("Anthropic 5 Workflow Patterns 对照表 (5-pattern Comparison)")
    print("=" * 90)
    for p in PATTERNS:
        print()
        print(f"📌 {p['name']} ({p['中文']})")
        print(f"   结构 (Structure): {p['结构']}")
        print(f"   何时用 (When):    {p['何时用']}")
        print(f"   仓库实现:          {p['本仓库']}")
        print(f"   成本/可控性:       {p['成本']} / {p['可控性']}")


def print_decision_tree() -> None:
    print("\n" + "=" * 90)
    print("决策树 (Decision Tree) — 拿到任务先问 5 个问题")
    print("=" * 90)
    print(
        """
    Q1. 任务是单一目标还是多步?
        单一 ──→ 看 Q3 / Q4
        多步 ──→ Q2

    Q2. 步骤之间是顺序依赖还是独立?
        顺序依赖 ──→ Prompt Chaining
        独立     ──→ Parallelization (Sectioning)
        动态分配 ──→ Orchestrator-Workers

    Q3. 输入是否需要先分流?
        是 ──→ Routing
        否 ──→ Q4

    Q4. 是否有清晰的"对错评估标准"?
        有 ──→ Evaluator-Optimizer (循环到通过)
        无 ──→ 单次 LLM 调用 (可能加 Voting 防错)

    Q5. 需要"多样化输出 / 减少幻觉"?
        是 ──→ Parallelization (Voting)
        否 ──→ 看上面其他答案
    """
    )


def print_quotes() -> None:
    print("=" * 90)
    print("Anthropic 大佬原文 (Key Anthropic Quotes)")
    print("=" * 90)
    print(
        """
    On simplicity (论简单):
      EN: "The most successful implementations weren't using complex frameworks
           or specialized libraries. Instead, they were building with simple,
           composable patterns."
      中文: 最成功的实现不是用复杂框架或专门库, 而是用简单可组合的模式.

    On when to choose Agent vs Workflow (何时该用 Agent):
      EN: "Use agents only when the task requires dynamic, autonomous behavior
           that cannot be achieved with predefined workflows."
      中文: 只有任务需要预定义工作流无法实现的动态自主行为时, 才用 Agent.

    On Evaluator-Optimizer (评估优化的关键):
      EN: "This workflow is particularly effective when we have clear evaluation
           criteria, and when iterative refinement provides measurable value."
      中文: 当评估标准清晰、迭代精炼有可衡量价值时, 这个模式最有效.
    """
    )


def main() -> None:
    print_table()
    print_decision_tree()
    print_quotes()


if __name__ == "__main__":
    main()

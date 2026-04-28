"""02 · Two-Agent Critique — 双 Agent 生成-批评.

Andrew Ng Reflection Pattern (Variant 2): Generator + Critic 两个独立 Agent.

vs 01 Self-Reflection:
    - 01: 同一 LLM 多轮自反思
    - 02: **两个独立 Agent**, 各自有不同 system_prompt + 可能不同 model

vs Ch6/03 Evaluator-Optimizer:
    - 那里是 chain 外部循环 (workflow)
    - 这里是 **agent 之间互动** (agent-to-agent dialogue)

教学要点:
    1. Generator Agent — 创作角色 (作者/工程师/客服)
    2. Critic Agent    — 严苛角色 (主编/审稿人/质检员)
    3. 两 Agent **轮流对话**, 每轮 critic 给反馈, generator 改

双业务:
    主 客服: Gen 客服 vs Critic 法务 (审合规)
    对照 数分: Gen 分析师 vs Critic CEO 视角 (审业务洞察)

Run:
    python 02_two_agent_critique.py
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
from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402


class GeneratorAgent:
    """Generator — 负责生成内容."""

    def __init__(self, role_prompt: str):
        self.llm = get_llm(temperature=0.5)
        self.role_prompt = role_prompt

    def generate(self, task: str, prev_critique: str = "") -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.role_prompt),
                (
                    "human",
                    "Task: {task}\n\n"
                    "Previous critic feedback (if any): {prev}\n\n"
                    "Output only your final response, no preamble.",
                ),
            ]
        )
        return (prompt | self.llm | StrOutputParser()).invoke(
            {"task": task, "prev": prev_critique or "(none, first attempt)"}
        )


class CriticAgent:
    """Critic — 严苛审核, 找问题."""

    def __init__(self, critic_prompt: str):
        # Critic 用 temperature=0 更严苛
        self.llm = get_llm(temperature=0.0)
        self.critic_prompt = critic_prompt

    def critique(self, task: str, generator_output: str) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.critic_prompt),
                (
                    "human",
                    "Task: {task}\n\nGenerator output: {output}\n\n"
                    "List your top 3 critiques + a 'pass/fail' verdict.\n"
                    "Format:\n"
                    "VERDICT: pass|fail\n"
                    "CRITIQUE 1: ...\n"
                    "CRITIQUE 2: ...\n"
                    "CRITIQUE 3: ...",
                ),
            ]
        )
        result = (prompt | self.llm | StrOutputParser()).invoke(
            {"task": task, "output": generator_output}
        )
        verdict = "fail"
        if "VERDICT: pass" in result.lower() or "verdict: pass" in result:
            verdict = "pass"
        return {"verdict": verdict, "feedback": result}


def two_agent_dialog(
    task: str, gen: GeneratorAgent, critic: CriticAgent, max_rounds: int = 3
) -> dict:
    """两 Agent 轮流对话直到 critic 通过 / max_rounds."""
    prev_critique = ""
    history = []

    for r in range(1, max_rounds + 1):
        print(f"\n  [Round {r}]")
        # Gen
        output = gen.generate(task, prev_critique)
        print(f"  [Gen]    {output[:100]}...")
        # Critic
        crit = critic.critique(task, output)
        print(f"  [Critic] {crit['verdict'].upper()}")
        for line in crit["feedback"].split("\n")[:5]:
            if line.strip():
                print(f"           {line[:100]}")

        history.append({"round": r, "gen": output, "critic": crit})

        if crit["verdict"] == "pass":
            print(f"  ✅ Round {r} Critic 通过")
            return {"final": output, "rounds": r, "history": history}

        prev_critique = crit["feedback"]

    return {
        "final": history[-1]["gen"],
        "rounds": max_rounds,
        "history": history,
        "max_rounds_hit": True,
    }


def main() -> None:
    print("=" * 70)
    print("Ch7 · 02 Two-Agent Critique — 双 Agent 互评 (Andrew Ng)")
    print("=" * 70)

    # ===== 主业务: 客服 vs 法务 =====
    print("\n--- [主业务] Customer Service Gen + Legal Critic ---")
    gen_cs = GeneratorAgent(
        "你是电商客服 Customer Service Rep. 友好,共情,简洁 ≤ 80 字回复."
    )
    critic_legal = CriticAgent(
        "你是公司法务 Legal Auditor. 严格审核客服回复, 红线:\n"
        "  - 不得包含'保证/绝对/100%/无条件赔偿'承诺词\n"
        "  - 不得对责任做过度承诺 (例: 误工费/精神损失)\n"
        "  - 必须有明确下一步动作\n"
        "  - 必须不卑不亢, 不过度道歉"
    )

    cs_task = "客户: 鞋子穿一次开胶, 我急着出差用, 现在错过会议! 必须 100% 退款 + 误工费!"
    print(f"客户消息: {cs_task}")
    cs_result = two_agent_dialog(cs_task, gen_cs, critic_legal, max_rounds=3)
    print(f"\n  最终: {cs_result['final'][:150]}")
    print(f"  通过轮数: {cs_result['rounds']}")

    # ===== 对照业务: 分析师 vs CEO =====
    print("\n\n--- [对照业务] Analyst Gen + CEO Critic ---")
    gen_da = GeneratorAgent(
        "你是数据分析师 Data Analyst. 写 100 字以内的销售洞察简报, 给非技术 CEO."
    )
    critic_ceo = CriticAgent(
        "你是 CEO. 你的标准:\n"
        "  - 一句话能说清核心 (lead with takeaway)\n"
        "  - 必须有具体数字 (不要'增长很多'这种空话)\n"
        "  - 必须有 1 个 actionable 建议\n"
        "  - 不要技术术语 (CEO 看不懂)"
    )

    da_task = (
        "数据: 上周销售 1500 单 (+25% YoY); 退货率 12% (前 6%); "
        "客单价 ¥320 (-5%); 投诉率 3.2% (前 1.5%). 给 CEO 写简报."
    )
    print(f"分析任务: {da_task[:100]}...")
    da_result = two_agent_dialog(da_task, gen_da, critic_ceo, max_rounds=3)
    print(f"\n  最终: {da_result['final'][:200]}")
    print(f"  通过轮数: {da_result['rounds']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 两 Agent 角色对立 (客服 vs 法务 / 分析师 vs CEO) → 反馈更尖锐")
    print("  - Critic temperature=0 更严苛, Gen temperature=0.5 更有创造性")
    print("  - 通过轮数因 task 而异: 简单任务 1 轮通过, 复杂的 2-3 轮")
    print("=" * 70)


if __name__ == "__main__":
    main()

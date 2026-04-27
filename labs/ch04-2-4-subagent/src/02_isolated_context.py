"""02 · SubAgent 上下文隔离演示.

为什么 SubAgent 重要? 因为它有"独立工作环境":
- 主 Agent 看到所有历史 messages, 容易上下文爆炸
- SubAgent 只收到一条任务描述, 干完返回结果, 不污染主 Agent

本脚本对比:
    场景 A: 不用 SubAgent, 主 Agent 自己干 5 件小事 — messages 列表会很长
    场景 B: 用 SubAgent 派发 5 件小事 — 主 Agent 看到的 messages 短得多

Run:
    python 02_isolated_context.py
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
from deepagents import SubAgent, create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# 5 个简单"独立"工具 (随机打分 / 等)
@tool
def score_topic(topic: str) -> int:
    """给某话题打 1-10 分.

    Args:
        topic: 话题
    """
    fake_scores = {
        "Python": 9,
        "Java": 8,
        "Go": 8,
        "Rust": 9,
        "JavaScript": 7,
    }
    return fake_scores.get(topic, 5)


def scenario_a_no_subagent() -> int:
    """场景 A: 主 Agent 自己跑 5 个工具调用."""
    print("\n--- 场景 A: 不用 SubAgent ---")
    agent = create_deep_agent(
        model=get_llm(),
        tools=[score_topic],
        system_prompt="给所有话题打分, 直接调 score_topic 5 次, 最后报告总分.",
    )
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="给以下 5 个话题打分: Python, Java, Go, Rust, JavaScript. 报告总分."
                )
            ]
        },
        config={"recursion_limit": 50},
    )
    msg_count = len(result["messages"])
    print(f"  主 Agent messages 总数: {msg_count}")
    return msg_count


def scenario_b_with_subagent() -> int:
    """场景 B: 用 SubAgent 派发."""
    print("\n--- 场景 B: 用 SubAgent ---")
    scorer = SubAgent(
        name="scorer",
        description="给单个话题打 1-10 分. 主 Agent 派一个话题给我, 我返回分数.",
        system_prompt="你是打分员, 用 score_topic 工具给指定话题打分, 只返回数字.",
        tools=[score_topic],
    )

    agent = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt=(
            "给定话题列表, 一个一个派给 scorer SubAgent 打分, "
            "拿到所有分数后求和报告."
        ),
        subagents=[scorer],
    )
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="给以下 5 个话题打分: Python, Java, Go, Rust, JavaScript. 报告总分."
                )
            ]
        },
        config={"recursion_limit": 50},
    )
    msg_count = len(result["messages"])
    print(f"  主 Agent messages 总数: {msg_count}")
    print(f"  (注: SubAgent 内部的 messages 不计入主 Agent)")
    return msg_count


def main() -> None:
    print("=" * 60)
    print("Ch4.2.4 · 02 SubAgent 上下文隔离")
    print("=" * 60)

    a = scenario_a_no_subagent()
    b = scenario_b_with_subagent()

    print("\n" + "=" * 60)
    print("对比:")
    print(f"  场景 A (主 Agent 自己跑 5 工具): messages = {a}")
    print(f"  场景 B (派给 SubAgent):          messages = {b}")
    if b < a:
        print(f"  ✅ SubAgent 节省了 {a - b} 条 messages (隔离生效)")
    else:
        print(f"  ⚠️  本次 SubAgent 没节省 (可能因任务太简单)")
    print()
    print("观察:")
    print("  - SubAgent 把'调工具+解析结果'封装到子 Agent 内")
    print("  - 主 Agent 只看到子 Agent 的最终返回 (而不是中间所有 ToolMessage)")
    print("  - 长任务下能显著节省主 Agent 的 token + 防上下文中毒")


if __name__ == "__main__":
    main()

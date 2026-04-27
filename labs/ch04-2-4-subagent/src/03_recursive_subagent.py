"""03 · SubAgent 派生 SubAgent — 树形分工.

主 Agent → 协调员 SubAgent → 执行员 SubAgent (递归 1 层)

教学要点:
    - 把任务分级: 顶层管 + 中层协调 + 基层执行
    - 协调员有自己的 SubAgent (执行员)
    - 上下文递归隔离: 顶层只看协调员的总结

实际上 deepagents 的 task tool 自然支持"主→子→孙"递归 — 只要 SubAgent 自己也声明
subagents 参数即可. 但更常见的姿势是把所有 SubAgent 都"扁平"挂在主 Agent 上, 让主
Agent 决定调度顺序. 本脚本演示扁平分工 (大部分场景的最佳实践).

Run:
    python 03_recursive_subagent.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "labs" / "ch03-frameworks-compare" / "src"))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from common_search import web_search  # noqa: E402
from deepagents import SubAgent, create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# ===== 工具 =====
@tool
def fetch_user_profile(user_id: str) -> str:
    """查询用户基本信息.

    Args:
        user_id: 用户 ID
    """
    fake = {
        "u001": "Alice, 30 岁, Java 工程师, 技术栈: Spring Boot",
        "u002": "Bob, 25 岁, 数据分析师, 技术栈: Python pandas",
        "u003": "Charlie, 35 岁, 产品经理, 技术栈: 需求分析",
    }
    return fake.get(user_id, "user not found")


@tool
def fetch_user_history(user_id: str) -> str:
    """查询用户最近 30 天行为日志.

    Args:
        user_id: 用户 ID
    """
    fake = {
        "u001": "登录 12 次, 提交 PR 8 个, 关注 LangChain 话题",
        "u002": "登录 25 次, 跑数据分析 50 次, 关注 LLM 应用",
        "u003": "登录 8 次, 主要看 PRD 评审",
    }
    return fake.get(user_id, "no history")


# ===== SubAgents (扁平挂主 Agent) =====
profile_lookup = SubAgent(
    name="profile_lookup",
    description="查询用户基本信息. 当需要某 user_id 的 profile 时派给我.",
    system_prompt="你是用户信息查询员, 调 fetch_user_profile 拿 user_id 的 profile, 简短返回.",
    tools=[fetch_user_profile],
)

history_lookup = SubAgent(
    name="history_lookup",
    description="查询用户行为历史. 当需要某 user_id 的最近活动时派给我.",
    system_prompt="你是行为分析员, 调 fetch_user_history 拿用户最近 30 天行为, 简短返回.",
    tools=[fetch_user_history],
)

researcher = SubAgent(
    name="researcher",
    description="联网调研某话题. 当需要外部资料/最新信息时派给我.",
    system_prompt="你是研究员, 用 web_search 搜 1-2 次相关内容, 列 3 条要点.",
    tools=[web_search],
)


def main() -> None:
    print("=" * 60)
    print("Ch4.2.4 · 03 多 SubAgent 编排 (扁平分工)")
    print("=" * 60)

    coordinator = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt=(
            "你是用户分析协调员. 给定一个 user_id 和一个推荐主题, 你的工作流:\n"
            "1. 派 profile_lookup 拿用户基本信息\n"
            "2. 派 history_lookup 拿用户行为历史\n"
            "3. 综合上面两步, 派 researcher 查这个推荐主题的相关资料\n"
            "4. 用 write_file 把'个性化推荐报告'写到 'recommendation.md' (≥ 200 字)\n"
            "5. 给用户一句话总结\n\n"
            "你不直接调工具, 全部派给 SubAgent 干."
        ),
        subagents=[profile_lookup, history_lookup, researcher],
    )

    task = "为用户 u001 生成一份个性化推荐, 主题=LangChain Agent 学习路径"
    print(f"\n任务: {task}\n")

    result = coordinator.invoke(
        {"messages": [HumanMessage(content=task)]},
        config={"recursion_limit": 30},
    )

    messages = result["messages"]
    files = result.get("files", {})

    # 统计 SubAgent 派发
    from collections import Counter

    subagent_calls: list[str] = []
    for m in messages:
        for tc in getattr(m, "tool_calls", []) or []:
            if tc.get("name") == "task":
                args = tc.get("args", {})
                subagent_calls.append(args.get("subagent_type", args.get("subagent", "?")))

    print("\n" + "=" * 60)
    print(f"主 Agent messages 总数: {len(messages)}")
    print(f"派发次数: {len(subagent_calls)}")
    for name, cnt in Counter(subagent_calls).items():
        print(f"  - {name}: {cnt} 次")
    print(f"虚拟 FS 文件: {list(files.keys())}")
    print("=" * 60)

    if "recommendation.md" in files:
        print("\n--- recommendation.md (前 500 字) ---")
        print(files["recommendation.md"][:500])

    print(f"\n最终回复: {messages[-1].content[:200]}")


if __name__ == "__main__":
    main()

"""01 · 主 Agent + 3 个 SubAgent 协作.

场景: 给一个研究问题, 三个专家协作输出研究报告.
- 研究员 (researcher): 联网搜资料
- 批评家 (critic): 审稿挑刺
- 写手 (writer): 整理成 markdown

主 Agent (项目经理) 用 task 工具派发, 不亲自下场写.

Run:
    python 01_three_role_agent.py
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
from common_search import web_search  # noqa: E402  复用 Ch3 的搜索工具
from deepagents import SubAgent, create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402


# ===== 三个 SubAgent 定义 =====
researcher = SubAgent(
    name="researcher",
    description=(
        "联网调研专家. 负责搜索关键资料并总结成 3-5 条要点. "
        "当需要查找事实/数据/最新信息时派给我."
    ),
    system_prompt=(
        "你是研究员. 用 web_search 搜索 1-2 次相关内容, 综合后列 3-5 条 bullet 要点. "
        "每个要点 < 30 字, 直接说事实, 不要叠加修饰. 输出纯 bullet 列表."
    ),
    tools=[web_search],
)

critic = SubAgent(
    name="critic",
    description=(
        "审稿专家. 负责挑刺找改进点. "
        "当一份草稿/报告需要质量把关时派给我."
    ),
    system_prompt=(
        "你是严苛的审稿人. 给定一段内容, 找 3 个具体的改进点 "
        "(每条要指出: 哪里 + 为什么有问题 + 改进建议). "
        "输出格式:\n"
        "1. [位置]: [问题] → [建议]\n"
        "2. ...\n"
        "3. ..."
    ),
)

writer = SubAgent(
    name="writer",
    description=(
        "技术写手. 负责把零散素材整理成结构化 markdown. "
        "当需要正式输出 (含小标题/列表) 时派给我."
    ),
    system_prompt=(
        "你是技术写手. 给定素材 + 任务, 输出一份完整 markdown:\n"
        "- 含 ## 一级 / ### 二级 标题\n"
        "- 用 - 列表 + 加粗关键词\n"
        "- 总长 200-400 字\n"
        "不要写 '以下是...' 这种引导语, 直接出内容."
    ),
)


def main() -> None:
    print("=" * 60)
    print("Ch4.2.4 · 01 三角色 SubAgent 协作")
    print("=" * 60)

    main_agent = create_deep_agent(
        model=get_llm(),
        tools=[web_search],
        system_prompt=(
            "你是项目经理. 收到研究任务后:\n"
            "1. 先派 researcher 调研, 拿回要点\n"
            "2. 再派 writer 把要点整理成 markdown 草稿\n"
            "3. 然后派 critic 审稿, 拿到 3 条改进\n"
            "4. 最后再派 writer 按改进出 v2 终稿\n"
            "5. 用 write_file 把终稿存到 'final_report.md'\n"
            "6. 给用户一句话总结\n\n"
            "你不要亲自下场写内容, 调度 SubAgent 干活."
        ),
        subagents=[researcher, critic, writer],
    )

    question = "DeepAgents 框架的 SubAgent 机制为什么能减少上下文污染?"
    print(f"\n研究问题: {question}\n")

    result = main_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"recursion_limit": 30},
    )

    messages = result["messages"]
    files = result.get("files", {})

    # 统计 task 调用 (派给 SubAgent)
    task_calls: list[str] = []
    for m in messages:
        for tc in getattr(m, "tool_calls", []) or []:
            if tc.get("name") == "task":
                # task 的 args 含 subagent name
                args = tc.get("args", {})
                subagent_name = args.get("subagent_type", args.get("subagent", "?"))
                task_calls.append(subagent_name)

    print("\n" + "=" * 60)
    print(f"消息总数        : {len(messages)}")
    print(f"工具调用 (含派发): {sum(1 for m in messages if isinstance(m, ToolMessage))}")
    print(f"task 派发次数   : {len(task_calls)}")
    if task_calls:
        from collections import Counter
        for name, cnt in Counter(task_calls).items():
            print(f"  - 派给 {name}: {cnt} 次")
    print(f"虚拟 FS 文件    : {list(files.keys())}")
    print("=" * 60)
    print("\n最终回复:")
    print(messages[-1].content[:300])

    if "final_report.md" in files:
        print("\n--- 终稿 final_report.md (前 500 字) ---")
        print(files["final_report.md"][:500])


if __name__ == "__main__":
    main()

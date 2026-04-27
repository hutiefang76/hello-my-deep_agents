"""01 · DeepAgents 最小 demo — 三参数三行启动.

教学要点:
    1. create_deep_agent(model, tools, system_prompt) 三参数
    2. 即使 tools=[] 不传任何自定义工具, Agent 也有 7 个内置工具
       (write_todos, read_file, write_file, edit_file, ls, glob, grep)
    3. agent.invoke() 返回的 result 含 messages + files (虚拟 FS)

Run:
    python 01_quickstart.py
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
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402


SYSTEM_PROMPT = """你是一名 DeepAgents 入门讲师. 用户问问题时:
1. 先用 write_todos 列出 2-3 步计划 (展示给用户看)
2. 用 write_file 把"教学笔记"写到 'notes.md' (≥ 100 字)
3. 最后用一句话给用户总结

教学目标: 让用户看到 DeepAgents 自动用了 todos 和 文件系统."""


def main() -> None:
    print("=" * 60)
    print("Ch4.1 · 01 DeepAgents 最小 demo (三参数)")
    print("=" * 60)

    # 第一参数: model — 通过 common.llm 工厂拿
    # 第二参数: tools — 不传任何自定义工具, 全部用内置的
    # 第三参数: system_prompt — 教 LLM 如何用工具
    agent = create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt=SYSTEM_PROMPT,
    )

    # 调用 — 输入是 HumanMessage 列表
    user_question = "请用 100 字介绍 DeepAgents 框架"
    print(f"\n用户提问: {user_question}\n")

    result = agent.invoke(
        {"messages": [HumanMessage(content=user_question)]},
        config={"recursion_limit": 15},
    )

    # 看看 Agent 干了啥
    messages = result["messages"]
    files = result.get("files", {})
    todos = result.get("todos", [])

    tool_calls_made: list[str] = []
    for m in messages:
        for tc in getattr(m, "tool_calls", []) or []:
            tool_calls_made.append(tc.get("name", ""))

    print("=" * 60)
    print(f"消息总数      : {len(messages)}")
    print(f"工具调用次数  : {sum(1 for m in messages if isinstance(m, ToolMessage))}")
    print(f"用到的工具    : {sorted(set(tool_calls_made))}")
    print(f"虚拟 FS 文件  : {list(files.keys())}")
    print(f"Todos         : {len(todos)} 条")
    if todos:
        for t in todos:
            print(f"  [{t.get('status', '?')}] {t.get('content', '?')}")
    print("=" * 60)
    print("\n最终答复:")
    print(messages[-1].content[:300])

    if files.get("notes.md"):
        print("\n--- 虚拟 FS notes.md (前 300 字) ---")
        print(files["notes.md"][:300])


if __name__ == "__main__":
    main()

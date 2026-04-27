"""02 · DeepAgents + 联网搜索工具.

在 01 的基础上加一个真实工具 web_search (复用 Ch3 的实现).
教学要点: 让学员看清"自定义工具如何接入 deepagents".

Run:
    python 02_with_search.py
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
from common_search import web_search  # noqa: E402  (复用 Ch3 的 web_search)
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402


SYSTEM_PROMPT = """你是一名研究助手. 工作流程:
1. 用 write_todos 列出研究步骤 (3-5 步)
2. 用 web_search 搜索 1-2 次相关信息
3. 用 write_file 把研究笔记写到 'research.md' (≥ 200 字 markdown)
4. 最后用 1-2 句话总结答复用户

注意: 搜索关键词要精准, 不要重复搜同一关键词."""


def main() -> None:
    print("=" * 60)
    print("Ch4.1 · 02 DeepAgents + 联网搜索")
    print("=" * 60)

    agent = create_deep_agent(
        model=get_llm(),
        tools=[web_search],          # ← 接入 Ch3 共享的搜索工具
        system_prompt=SYSTEM_PROMPT,
    )

    question = "LangGraph 和 DeepAgents 有什么关系?"
    print(f"\n用户提问: {question}\n")

    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"recursion_limit": 20},
    )

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
    print(f"Todos 数量    : {len(todos)}")
    print("=" * 60)
    print("\n最终答复 (前 300 字):")
    print(messages[-1].content[:300])

    if "research.md" in files:
        print("\n--- 虚拟 FS research.md (前 400 字) ---")
        print(files["research.md"][:400])


if __name__ == "__main__":
    main()

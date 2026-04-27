"""03 · DeepAgents 实现 — 三参数启动, 自带 Planning + FS + SubAgent.

特点:
    - create_deep_agent(model, tools, instructions) 一行启动
    - 自带:
        * Planning Tool (write_todos): LLM 自己列任务清单并标记完成
        * Virtual File System (read_file/write_file/edit_file/ls): 中间结果落"盘"
        * SubAgent: 派生子 Agent 处理隔离任务
        * Detailed System Prompt: 内置长指令模板
    - 代码 ~50 行 — 对比上面两个看到工程化抽象的"段位差"

类比:
    LangChain  ≈ Spring Framework        (积木)
    LangGraph  ≈ Spring StateMachine     (状态机)
    DeepAgents ≈ Spring Boot Starter     (开箱即用)

Run:
    python 03_deepagents.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from common.llm import get_llm  # noqa: E402
from common_search import RESEARCH_QUESTION, web_search  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402


INSTRUCTIONS = """你是一名严谨的研究助手. 流程:
1. 先用 write_todos 把研究步骤列出来 (3-5 步)
2. 用 web_search 搜索 1-2 次
3. 用 write_file 把研究报告写到 'report.md' (≥ 200 字 markdown)
4. 最后用一句话总结答复用户

注意保持步骤清晰, 必要时更新 todos."""


def main() -> None:
    print("=" * 60)
    print("Ch3 · 03 DeepAgents (一行启动)")
    print("=" * 60)
    print(f"研究问题: {RESEARCH_QUESTION}\n")

    # 这就是全部代码 — 三个参数搞定
    # (deepagents 0.5+ 用 system_prompt; 0.0.x 用 instructions, 注意版本)
    agent = create_deep_agent(
        model=get_llm(),
        tools=[web_search],     # write_todos / read_file / write_file 等内置, 不用自己写
        system_prompt=INSTRUCTIONS,
    )

    t0 = time.perf_counter()
    result = agent.invoke(
        {"messages": [HumanMessage(content=f"研究问题: {RESEARCH_QUESTION}")]},
        config={"recursion_limit": 25},
    )
    elapsed = time.perf_counter() - t0

    messages = result["messages"]
    final = messages[-1].content
    tool_calls = sum(1 for m in messages if isinstance(m, ToolMessage))

    # 看看 Agent 用了哪些内置工具
    used_tools: set[str] = set()
    for m in messages:
        for tc in getattr(m, "tool_calls", []) or []:
            used_tools.add(tc.get("name", ""))

    # 看看 virtual fs 里有啥
    files = result.get("files", {})

    print("\n" + "=" * 60)
    print(f"工具调用    : {tool_calls} 次")
    print(f"用到的工具  : {sorted(used_tools)}")
    print(f"虚拟文件    : {list(files.keys())}")
    print(f"耗时        : {elapsed:.1f}s")
    print(f"消息总数    : {len(messages)}")
    print("=" * 60)
    print("最终答案 (前 500 字):")
    print(final[:500])

    if "report.md" in files:
        print("\n--- 虚拟 FS 中的 report.md (前 500 字) ---")
        print(files["report.md"][:500])

    print(f"\n>>> METRICS deepagents tools={tool_calls} elapsed={elapsed:.1f} "
          f"used={','.join(sorted(used_tools))}")


if __name__ == "__main__":
    main()

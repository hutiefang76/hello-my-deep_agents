"""01 · 纯 LangChain 实现 — 手动拼装研究 Agent.

特点:
    - 所有控制流自己写 (循环、停止条件、消息管理)
    - 用 LCEL 拼 prompt | llm | parser
    - 工具调用循环手写 (上节 Ch2/04 见过)

代码量预估 ~150 行 — 看清"乐高积木"长什么样.

Run:
    python 01_langchain_only.py
"""

from __future__ import annotations

import json
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
from common_search import RESEARCH_QUESTION, TOOLS  # noqa: E402
from langchain_core.messages import (  # noqa: E402
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)


SYSTEM_PROMPT = """你是一名研究助手. 用户提出研究问题后, 你的工作流程:
1. 用 web_search 工具搜索 1-2 次相关信息
2. 综合搜到的内容, 形成结构化报告
3. 用 write_report 工具输出最终报告 (含标题 + 完整 markdown 内容)
4. 最后给用户一句话总结

工具调用循环最多 5 步, 报告必须 ≥ 200 字. 禁止重复搜同一关键词."""


def run_research(question: str) -> dict:
    """跑一轮研究 — 返回 (步数, 工具调用次数, 最终答案, 耗时)."""
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages: list = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"研究问题: {question}"),
    ]

    tool_call_count = 0
    t0 = time.perf_counter()

    for step in range(8):  # 防死循环
        ai_msg: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:
            elapsed = time.perf_counter() - t0
            return {
                "steps": step + 1,
                "tool_calls": tool_call_count,
                "final": ai_msg.content,
                "elapsed_sec": elapsed,
                "messages": messages,
            }

        # 手动执行所有工具调用
        for tc in ai_msg.tool_calls:
            tool_call_count += 1
            tool_name = tc["name"]
            tool_args = tc["args"]
            print(f"  [step {step}] 调 {tool_name}({list(tool_args.keys())})")

            tool_fn = next(t for t in TOOLS if t.name == tool_name)
            try:
                result = tool_fn.invoke(tool_args)
            except Exception as e:
                result = f"工具调用异常: {e}"

            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False)
                    if not isinstance(result, str)
                    else result,
                    tool_call_id=tc["id"],
                )
            )

    return {
        "steps": 8,
        "tool_calls": tool_call_count,
        "final": "[超出 8 步未收敛]",
        "elapsed_sec": time.perf_counter() - t0,
        "messages": messages,
    }


def main() -> None:
    print("=" * 60)
    print("Ch3 · 01 LangChain only (手动拼装)")
    print("=" * 60)
    print(f"研究问题: {RESEARCH_QUESTION}\n")

    result = run_research(RESEARCH_QUESTION)

    print("\n" + "=" * 60)
    print(f"步数        : {result['steps']}")
    print(f"工具调用    : {result['tool_calls']} 次")
    print(f"耗时        : {result['elapsed_sec']:.1f}s")
    print(f"消息总数    : {len(result['messages'])}")
    print("=" * 60)
    print("最终答案 (前 500 字):")
    print(result["final"][:500])

    # 把指标写到 stdout 供 verify.sh 抓
    print(f"\n>>> METRICS langchain_only steps={result['steps']} "
          f"tools={result['tool_calls']} elapsed={result['elapsed_sec']:.1f}")


if __name__ == "__main__":
    main()

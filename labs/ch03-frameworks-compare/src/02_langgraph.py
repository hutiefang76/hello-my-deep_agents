"""02 · LangGraph 实现 — 状态机版研究 Agent.

特点:
    - 显式声明状态 (TypedDict)
    - 节点 (node) + 边 (edge), 用图描述工作流
    - 支持断点续跑 (Checkpointer)
    - 支持 stream_mode='updates' 实时看每步

实际上用 langgraph.prebuilt.create_react_agent 就一行 — 但本脚本演示
"自己拼图" 的过程, 让学员看清状态机的样子.

Run:
    python 02_langgraph.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import TypedDict

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
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.graph.message import add_messages  # noqa: E402

from typing_extensions import Annotated  # noqa: E402


# ===== 1. 定义状态 =====
class AgentState(TypedDict):
    """状态 = messages 列表 (用 add_messages reducer 自动追加)."""

    messages: Annotated[list[AnyMessage], add_messages]


# ===== 2. 节点: 让 LLM 决策 (调工具 or 给答案) =====
def call_llm(state: AgentState) -> dict:
    """节点 1: 调 LLM, 让它决定下一步."""
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ===== 3. 节点: 执行工具 =====
def call_tools(state: AgentState) -> dict:
    """节点 2: 拿出最新 AIMessage 的 tool_calls, 真实执行."""
    last_msg: AIMessage = state["messages"][-1]  # type: ignore[assignment]
    new_messages: list[AnyMessage] = []
    for tc in last_msg.tool_calls:
        print(f"  [graph] 调 {tc['name']}({list(tc['args'].keys())})")
        tool_fn = next(t for t in TOOLS if t.name == tc["name"])
        try:
            result = tool_fn.invoke(tc["args"])
        except Exception as e:
            result = f"工具异常: {e}"
        new_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tc["id"],
            )
        )
    return {"messages": new_messages}


# ===== 4. 条件边: 决定走 tool 节点还是 END =====
def should_continue(state: AgentState) -> str:
    """条件函数 — 看最后一条消息是否带 tool_calls."""
    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"
    return END


# ===== 5. 构图 =====
def build_graph():
    workflow = StateGraph(AgentState)

    # 加节点
    workflow.add_node("llm", call_llm)
    workflow.add_node("tools", call_tools)

    # 加边: START → llm
    workflow.add_edge(START, "llm")

    # 条件边: llm → tools (如果有 tool_calls) 或 → END
    workflow.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})

    # tools 跑完回 llm 节点 (经典 ReAct 循环)
    workflow.add_edge("tools", "llm")

    return workflow.compile()


SYSTEM_PROMPT = """你是研究助手. 用 web_search 搜 1-2 次, 然后用 write_report 写
出 ≥ 200 字的 markdown 报告, 最后给用户一句话总结. 工具调用最多 5 次."""


def main() -> None:
    print("=" * 60)
    print("Ch3 · 02 LangGraph (状态机)")
    print("=" * 60)
    print(f"研究问题: {RESEARCH_QUESTION}\n")

    graph = build_graph()

    initial = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"研究问题: {RESEARCH_QUESTION}"),
        ]
    }

    t0 = time.perf_counter()
    result = graph.invoke(initial, config={"recursion_limit": 15})
    elapsed = time.perf_counter() - t0

    final = result["messages"][-1].content
    tool_calls = sum(
        1 for m in result["messages"] if isinstance(m, ToolMessage)
    )

    print("\n" + "=" * 60)
    print(f"工具调用    : {tool_calls} 次")
    print(f"耗时        : {elapsed:.1f}s")
    print(f"消息总数    : {len(result['messages'])}")
    print("=" * 60)
    print("最终答案 (前 500 字):")
    print(final[:500])

    print(f"\n>>> METRICS langgraph tools={tool_calls} elapsed={elapsed:.1f}")


if __name__ == "__main__":
    main()

"""05 · ReAct Agent (LangGraph 官方版) — 一行代替手写循环.

上节脚本手写的循环, LangGraph 官方一行就搞定:
    agent = create_react_agent(model, tools, prompt)

这是 LangChain AI 推荐的 Agent 起手式 — 比 langchain.agents 老 API 更稳定.

Run:
    python 05_react_agent.py
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
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langgraph.prebuilt import create_react_agent  # noqa: E402


# ===== 工具定义 (复用上节的) =====
@tool
def get_weather(city: str) -> str:
    """查询某城市的实时天气. 仅支持: 北京 / 上海 / 广州 / 杭州.

    Args:
        city: 城市名
    """
    fake_db = {
        "北京": "26°C, 晴, 风力 3 级",
        "上海": "29°C, 多云, 湿度 65%",
        "广州": "32°C, 阵雨, 注意带伞",
        "杭州": "28°C, 晴, 适合户外",
    }
    return fake_db.get(city, f"{city}: 数据库无此城市数据")


@tool
def calculate(expression: str) -> str:
    """计算简单数学表达式. 仅支持 +, -, *, /, (), 数字.

    Args:
        expression: 数学表达式字符串
    """
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"错误: 表达式包含不允许的字符"
    try:
        return f"结果: {eval(expression, {'__builtins__': {}}, {})}"  # noqa: S307
    except Exception as e:
        return f"计算失败: {e}"


@tool
def search_user(user_id: str) -> str:
    """根据 user_id 查询用户基本信息.

    Args:
        user_id: 用户 ID
    """
    fake_db = {
        "u001": "Alice (30 岁, admin)",
        "u002": "Bob (25 岁, user)",
    }
    return fake_db.get(user_id, "user not found")


TOOLS = [get_weather, calculate, search_user]


def demo_react_agent() -> None:
    """LangGraph 官方 create_react_agent — 一行代替手写循环."""
    print("--- create_react_agent: 一行启动 ReAct Agent ---")

    llm = get_llm()

    # 一行启 Agent — 内置 ReAct 循环, 自动管 messages 和 tool_calls
    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt="你是一名能调用工具的助手. 用户问问题, 你判断要不要调工具, 调完给简洁答案.",
    )

    # 单次调用
    print("\n问题 1: 杭州天气怎么样?")
    result = agent.invoke({"messages": [HumanMessage(content="杭州天气怎么样?")]})
    final_msg = result["messages"][-1]
    print(f"最终答案: {final_msg.content}")
    print(f"消息总数: {len(result['messages'])} (含 tool_calls 和 tool_message)")

    # 多步问题 (Agent 自动多次调工具)
    print("\n问题 2: 北京和上海哪个更热? 然后帮我算下温差")
    result = agent.invoke(
        {"messages": [HumanMessage(content="北京和上海现在哪个更热? 然后算一下温差")]}
    )
    print(f"\n最终答案: {result['messages'][-1].content}")
    print(f"消息总数: {len(result['messages'])} (Agent 自动多步调工具)")


def demo_stream_react() -> None:
    """流式跑 Agent — 看到每一步的中间过程."""
    print("\n--- 流式调用 — 实时看 Agent 推理过程 ---")
    agent = create_react_agent(
        model=get_llm(),
        tools=TOOLS,
        prompt="你是工具型助手, 必要时调工具, 给简洁答案.",
    )

    print("\n问题: u001 是谁? 然后查广州天气")
    for step in agent.stream(
        {"messages": [HumanMessage(content="u001 是谁? 然后查广州天气")]},
        stream_mode="updates",
    ):
        for node_name, node_output in step.items():
            print(f"\n[{node_name}]")
            if "messages" in node_output:
                for m in node_output["messages"]:
                    msg_type = type(m).__name__
                    content = getattr(m, "content", "")
                    tool_calls = getattr(m, "tool_calls", None)
                    if tool_calls:
                        print(f"  {msg_type}: 调工具 {[tc['name'] for tc in tool_calls]}")
                    elif content:
                        print(f"  {msg_type}: {content[:100]}...")


def main() -> None:
    print("=" * 60)
    print("Ch2 · 05 ReAct Agent (LangGraph 官方)")
    print("=" * 60)

    demo_react_agent()
    demo_stream_react()

    print("\n--- 关键点 ---")
    print("  - create_react_agent(model, tools, prompt) 一行启动 Agent")
    print("  - agent.invoke({'messages': [...]}) 同步全跑")
    print("  - agent.stream(..., stream_mode='updates') 流式看每步")
    print("  - 内置 ReAct 循环, 不用自己写 while + tool_calls 解析")
    print("  - 这是后续 Ch4 DeepAgents 的基础 — DeepAgents 在此之上加 Planning/SubAgent/FS")


if __name__ == "__main__":
    main()

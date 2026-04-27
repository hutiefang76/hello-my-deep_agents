"""04 · 工具调用 (Function Calling) — LLM 主动调你的代码.

核心机制:
    1. 你用 @tool 装饰器把 Python 函数标为"可被 LLM 调用的工具"
    2. llm.bind_tools([...]) 把工具描述塞进 LLM 的请求
    3. LLM 不会自己执行函数, 而是返回 tool_calls (函数名 + 参数)
    4. 你的代码真实执行, 把结果回传给 LLM
    5. LLM 看到结果后给最终答案

教学要点:
    - @tool 装饰器
    - tool.invoke(args) 直接执行
    - llm.bind_tools 让 LLM 知道有哪些工具
    - tool_calls 提取
    - 完整 ReAct 循环 (手写版, 下个脚本看官方简化版)

Run:
    python 04_tool_call.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# ===== 1. 用 @tool 装饰器定义工具 =====
@tool
def get_weather(city: str) -> str:
    """查询某城市的实时天气. 返回字符串描述.

    Args:
        city: 城市名, 如 "北京", "上海", "广州"
    """
    # 演示用 mock 数据 — 真实场景会调和风/AccuWeather API
    fake_db = {
        "北京": "26°C, 晴, 风力 3 级",
        "上海": "29°C, 多云, 湿度 65%",
        "广州": "32°C, 阵雨, 注意带伞",
        "杭州": "28°C, 晴, 适合户外",
    }
    return fake_db.get(city, f"{city}: 数据库无此城市数据")


@tool
def calculate(expression: str) -> str:
    """计算一个简单的数学表达式. 仅支持 +, -, *, /, (), 数字.

    Args:
        expression: 数学表达式字符串, 如 "2+3*4"
    """
    # 安全起见, 限制只能是数字和运算符
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"错误: 表达式包含不允许的字符 — {expression}"
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return f"结果: {result}"
    except Exception as e:
        return f"计算失败: {e}"


@tool
def search_user(user_id: str) -> dict:
    """根据 user_id 查询用户基本信息.

    Args:
        user_id: 用户 ID, 如 "u001"
    """
    fake_db = {
        "u001": {"name": "Alice", "age": 30, "role": "admin"},
        "u002": {"name": "Bob", "age": 25, "role": "user"},
    }
    return fake_db.get(user_id, {"error": "user not found"})


TOOLS = [get_weather, calculate, search_user]


def demo_tool_invoke_directly() -> None:
    """1. 工具能直接当函数调 — 调试时常用."""
    print("--- 1. 工具直接调用 (不通过 LLM) ---")
    print(f"get_weather.invoke('北京')         = {get_weather.invoke('北京')}")
    print(f"calculate.invoke('(1+2)*3')         = {calculate.invoke('(1+2)*3')}")
    print(f"search_user.invoke('u001')          = {search_user.invoke('u001')}")
    print()


def demo_llm_decides_tool() -> None:
    """2. LLM 看问题, 决定调哪个工具 — 但还没真的执行."""
    print("--- 2. LLM 决策调哪个工具 (返回 tool_calls, 还没执行) ---")
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    questions = [
        "北京今天天气怎么样?",
        "(15+8)*3 等于多少?",
        "u001 是谁?",
    ]

    for q in questions:
        resp = llm_with_tools.invoke([HumanMessage(content=q)])
        print(f"问: {q}")
        if resp.tool_calls:
            for tc in resp.tool_calls:
                print(f"  → LLM 决定调 {tc['name']}({tc['args']})")
        else:
            print(f"  → LLM 直接回答: {resp.content[:60]}...")
        print()


def demo_full_react_loop() -> None:
    """3. 完整 ReAct 循环 — 手写版.

    流程:
        1. user 提问
        2. LLM 决定调工具
        3. 执行工具
        4. 把结果塞回去
        5. LLM 给最终答案
    """
    print("--- 3. 完整 ReAct 循环 (手写, 下个脚本看官方简化版) ---")
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages: list = [
        SystemMessage(content="你是一个能调用工具的助手. 必要时调工具, 然后给用户简洁答案."),
        HumanMessage(content="帮我查一下 u001 是谁? 顺便算一下 (12+8)*5 等于多少?"),
    ]

    # 循环最多 5 轮防死循环
    for step in range(5):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:
            print(f"[Step {step}] LLM 给最终答案: {ai_msg.content}")
            break

        print(f"[Step {step}] LLM 想调 {len(ai_msg.tool_calls)} 个工具")
        # 执行所有工具调用
        for tc in ai_msg.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            print(f"  → 执行 {tool_name}({tool_args})")

            # 找到对应的 tool 对象
            tool_fn = next(t for t in TOOLS if t.name == tool_name)
            result = tool_fn.invoke(tool_args)
            print(f"  ← 结果: {result!r}"[:100])

            # 把结果塞回 messages
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False)
                    if not isinstance(result, str)
                    else result,
                    tool_call_id=tc["id"],
                )
            )


def main() -> None:
    print("=" * 60)
    print("Ch2 · 04 工具调用 (Function Calling)")
    print("=" * 60)

    demo_tool_invoke_directly()
    demo_llm_decides_tool()
    demo_full_react_loop()

    print("\n--- 关键点 ---")
    print("  - @tool 装饰器把 Python 函数标记为可被 LLM 调用")
    print("  - llm.bind_tools 把工具描述塞进 LLM 请求")
    print("  - LLM 返回 tool_calls 而不是直接执行")
    print("  - 你的代码 (或 framework) 负责真实执行 + 回传结果")
    print("  - 完整循环就是 ReAct (Reasoning + Acting)")


if __name__ == "__main__":
    main()

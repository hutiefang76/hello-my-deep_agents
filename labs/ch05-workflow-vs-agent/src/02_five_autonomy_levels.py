"""02 · Five Levels of Autonomy — 自主性 5 级阶梯.

Based on Harrison Chase's "Cognitive Architectures" framework.

Same task ("greet user with personalized message based on time"):
    L1 Hardcoded:  if-else by hour
    L2 Single Call: LLM 一次性出问候语
    L3 Chain:       LLM 写大纲 → LLM 填细节
    L4 Router:      LLM 选 'morning|afternoon|evening' → 走对应分支
    L5 Agent:       Agent 自己决定查时间/查天气/查日历

Run:
    python 02_five_autonomy_levels.py
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# ============================================================
# L1 · Hardcoded (硬编码) — No LLM
# ============================================================
def level_1_hardcoded(user_name: str) -> str:
    """L1: 完全硬编码, 0 LLM 调用."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        period = "Good morning"
    elif 12 <= hour < 18:
        period = "Good afternoon"
    else:
        period = "Good evening"
    return f"{period}, {user_name}!"


# ============================================================
# L2 · Single LLM Call (单次调用) — 1 LLM
# ============================================================
def level_2_single_call(user_name: str) -> str:
    """L2: 单次 LLM 调用, 让 LLM 自己决定问候内容."""
    llm = get_llm()
    response = llm.invoke(
        f"Generate a personalized greeting for user '{user_name}'. "
        f"Current hour is {datetime.now().hour}. Reply in one sentence."
    )
    return response.content


# ============================================================
# L3 · LLM Chain (链) — Multiple LLM in fixed order
# ============================================================
def level_3_chain(user_name: str) -> str:
    """L3: 固定 chain — outline → detail."""
    llm = get_llm()
    parser = StrOutputParser()

    outline_prompt = ChatPromptTemplate.from_template(
        "Suggest 3 keywords for greeting user {name} at hour {hour}. Comma-separated."
    )
    detail_prompt = ChatPromptTemplate.from_template(
        "Using these keywords: {keywords}, write a warm 1-sentence greeting for {name}."
    )

    outline_chain = outline_prompt | llm | parser
    keywords = outline_chain.invoke({"name": user_name, "hour": datetime.now().hour})

    detail_chain = detail_prompt | llm | parser
    return detail_chain.invoke({"keywords": keywords, "name": user_name})


# ============================================================
# L4 · LLM Router (路由) — LLM picks branch
# ============================================================
from typing import Literal  # noqa: E402

from pydantic import BaseModel, Field  # noqa: E402


class TimeOfDay(BaseModel):
    period: Literal["morning", "afternoon", "evening", "night"]
    formality: Literal["casual", "formal"] = Field(description="问候语风格")


def level_4_router(user_name: str) -> str:
    """L4: LLM 选择走哪个分支."""
    llm = get_llm(temperature=0.0)
    structured = llm.with_structured_output(TimeOfDay)

    decision = structured.invoke(
        f"Given hour={datetime.now().hour} and user={user_name}, classify the time period and "
        f"recommend formality."
    )

    # 不同分支不同 prompt
    handlers = {
        "morning": f"Energetic morning greeting for {user_name}",
        "afternoon": f"Brief afternoon check-in for {user_name}",
        "evening": f"Relaxing evening greeting for {user_name}",
        "night": f"Quiet night greeting for {user_name}",
    }
    style = "casual" if decision.formality == "casual" else "formal"

    response = llm.invoke(f"{handlers[decision.period]}. Style: {style}. One sentence.")
    return response.content


# ============================================================
# L5 · Autonomous Agent (自主智能体) — Agent decides everything
# ============================================================
@tool
def get_current_time() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat(timespec="seconds")


@tool
def get_user_profile(user_name: str) -> str:
    """Look up user preferences (timezone, language, last-seen).

    Args:
        user_name: User's name
    """
    fake_db = {
        "Alice": "timezone=UTC+8, language=zh, last_seen=2 hours ago, status=working",
        "Bob": "timezone=UTC-5, language=en, last_seen=1 day ago, status=offline",
    }
    return fake_db.get(user_name, "User not found, treat as default English speaker")


def level_5_autonomous(user_name: str) -> tuple[str, dict]:
    """L5: 完全自主 Agent — 自己决定查什么/调什么工具."""
    agent = create_deep_agent(
        model=get_llm(),
        tools=[get_current_time, get_user_profile],
        system_prompt=(
            "You are a personalization expert. Given a user name, decide what info you need "
            "(time, profile, etc.), call tools, then craft a personalized greeting in 1-2 "
            "sentences. Match user's language preference."
        ),
    )

    result = agent.invoke(
        {"messages": [HumanMessage(content=f"Greet user '{user_name}'")]},
        config={"recursion_limit": 10},
    )
    msgs = result["messages"]
    tool_calls = sum(1 for m in msgs if isinstance(m, ToolMessage))
    return msgs[-1].content, {"messages": len(msgs), "tool_calls": tool_calls}


# ============================================================
# 对比 Demo
# ============================================================
def benchmark(level_fn, user_name: str, level_name: str) -> dict:
    t0 = time.perf_counter()
    try:
        result = level_fn(user_name)
        if isinstance(result, tuple):
            output, extra = result
        else:
            output, extra = result, {}
        elapsed = time.perf_counter() - t0
        return {
            "level": level_name,
            "elapsed_sec": round(elapsed, 2),
            "output": output[:120],
            **extra,
        }
    except Exception as e:
        return {"level": level_name, "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    print("=" * 70)
    print("Ch5 · 02 Five Autonomy Levels — 5 自主性等级 (Chase framework)")
    print("=" * 70)

    user = "Alice"
    print(f"\n任务: 给 {user} 生成个性化问候\n")

    runs = [
        (level_1_hardcoded, "L1 Hardcoded"),
        (level_2_single_call, "L2 Single Call"),
        (level_3_chain, "L3 Chain"),
        (level_4_router, "L4 Router"),
        (level_5_autonomous, "L5 Autonomous Agent"),
    ]

    print(f"{'Level':<22} {'耗时':<8} {'调用':<8} {'输出 (前 80 字)'}")
    print("-" * 90)
    for fn, name in runs:
        out = benchmark(fn, user, name)
        if "error" in out:
            print(f"{name:<22} ERROR: {out['error']}")
            continue
        msgs = out.get("messages", "-")
        tc = out.get("tool_calls", 0)
        msgs_str = f"{msgs}msg/{tc}tc" if msgs != "-" else "-"
        print(f"{name:<22} {out['elapsed_sec']}s    {msgs_str:<8} {out['output'][:80]}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  L1 0 LLM, 0 cost, 0 灵活性")
    print("  L2 1 LLM, 极低 cost, 有限灵活性")
    print("  L3 2 LLM, 低 cost, 中灵活性 (可拆解步骤)")
    print("  L4 1+1 LLM, 中 cost, 高灵活性 (按意图分流)")
    print("  L5 N×LLM + 工具, 高 cost, 完全灵活 (Agent 自决)")
    print()
    print("Chase 建议 (Chase's advice):")
    print("  '从 L1 起步, 必要时升级. 别一上来就 L5.'")
    print("  'Start at L1, upgrade only when needed. Don't jump to L5 immediately.'")
    print("=" * 70)


if __name__ == "__main__":
    main()

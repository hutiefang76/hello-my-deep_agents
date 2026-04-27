"""01 · 自定义工具进阶 — 复杂参数 / 返回类型 / 异常处理.

教学要点:
    1. Pydantic args_schema 让工具入参更结构化
    2. 工具返回 dict / Pydantic 对象 (不只是字符串)
    3. 抛业务异常 → LLM 看到错误后会重试或换工具
    4. 工具描述 (docstring) 是 LLM 唯一的"使用说明书", 一定要写好

Run:
    python 01_custom_tool.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ===== 1. 简单工具 (Ch2 见过) =====
@tool
def get_current_time() -> str:
    """获取当前时间. 返回 ISO 8601 格式字符串."""
    return datetime.now().isoformat(timespec="seconds")


# ===== 2. 复杂工具: Pydantic args_schema =====
class OrderArgs(BaseModel):
    """订单查询入参."""

    order_id: str = Field(description="订单 ID, 如 O20260427")
    fields: list[Literal["status", "items", "delivery", "amount"]] = Field(
        default=["status"],
        description="要查的字段, 多选自 status/items/delivery/amount",
    )


@tool(args_schema=OrderArgs)
def query_order_advanced(order_id: str, fields: list[str]) -> dict:
    """查询订单详情 (按字段定制).

    可选字段: status (订单状态) / items (商品列表) / delivery (物流) / amount (金额).
    """
    # 模拟订单数据库
    fake_db = {
        "O20260427": {
            "status": "配送中",
            "items": [
                {"name": "羽绒服", "qty": 1, "price": 599.0},
                {"name": "围巾", "qty": 2, "price": 99.0},
            ],
            "delivery": {"company": "顺丰", "tracking": "SF1234567", "eta": "明日 18:00 前"},
            "amount": {"product": 797.0, "shipping": 0.0, "discount": 50.0, "total": 747.0},
        },
        "O20260428": {
            "status": "已签收",
            "items": [{"name": "运动鞋", "qty": 1, "price": 399.0}],
            "delivery": {"company": "京东", "tracking": "JD7777", "eta": "已送达"},
            "amount": {"product": 399.0, "shipping": 0.0, "discount": 0.0, "total": 399.0},
        },
    }

    if order_id not in fake_db:
        # 抛 ValueError, LLM 看到会重试或换工具
        raise ValueError(f"订单 {order_id} 不存在")

    full = fake_db[order_id]
    # 只返回请求的字段 (节省 token)
    return {f: full[f] for f in fields if f in full}


# ===== 3. 工具返回 Pydantic 对象 (LLM 也认) =====
class WeatherReport(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int


@tool
def get_weather(city: str) -> WeatherReport:
    """查询某城市天气, 返回结构化对象."""
    fake = {
        "北京": WeatherReport(city="北京", temperature=26.0, condition="晴", humidity=45),
        "上海": WeatherReport(city="上海", temperature=29.0, condition="多云", humidity=65),
    }
    if city not in fake:
        raise ValueError(f"暂不支持城市: {city}")
    return fake[city]


# ===== 4. 工具直接调试 (不通过 LLM) =====
def demo_direct_invoke() -> None:
    print("--- 1. 工具直接调用 (调试用) ---")

    # 简单工具
    print(f"get_current_time()  = {get_current_time.invoke({})}")

    # 复杂工具
    result = query_order_advanced.invoke(
        {"order_id": "O20260427", "fields": ["status", "amount"]}
    )
    print(f"query_order_advanced ={result}")

    # 异常分支
    try:
        query_order_advanced.invoke({"order_id": "O999", "fields": ["status"]})
    except Exception as e:
        print(f"order O999 (预期异常): {type(e).__name__}: {e}")


# ===== 5. 通过 LLM 调用工具 =====
def demo_via_llm() -> None:
    print("\n--- 2. LLM 决定调哪个工具 ---")
    llm = get_llm()
    llm_with_tools = llm.bind_tools([get_current_time, query_order_advanced, get_weather])

    questions = [
        "现在几点?",
        "查一下订单 O20260428 的状态和物流",
        "上海天气怎么样?",
        "查订单 O999",  # 故意失败, 看 LLM 怎么处理
    ]

    for q in questions:
        print(f"\n问: {q}")
        resp = llm_with_tools.invoke([HumanMessage(content=q)])
        if resp.tool_calls:
            for tc in resp.tool_calls:
                print(f"  → LLM 调 {tc['name']}({tc['args']})")
                # 真实执行
                tool_fn = next(
                    t
                    for t in [get_current_time, query_order_advanced, get_weather]
                    if t.name == tc["name"]
                )
                try:
                    result = tool_fn.invoke(tc["args"])
                    print(f"  ← 结果: {result}"[:150])
                except Exception as e:
                    print(f"  ← 异常: {type(e).__name__}: {e}")
        else:
            print(f"  → LLM 直答: {resp.content[:80]}")


def main() -> None:
    print("=" * 60)
    print("Ch4.2.3 · 01 自定义工具进阶")
    print("=" * 60)
    demo_direct_invoke()
    demo_via_llm()


if __name__ == "__main__":
    main()

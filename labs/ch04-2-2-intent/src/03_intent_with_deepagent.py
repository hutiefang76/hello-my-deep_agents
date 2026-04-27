"""03 · DeepAgent + 意图识别 — 前置分流让 DeepAgent 更聚焦.

为什么不直接让 DeepAgent 自己判断意图? 因为:
    - DeepAgent 自己的 system_prompt 已经很长 (含 Planning/FS/SubAgent 指令)
    - 把意图分类逻辑外置, 让 DeepAgent 只关注"在已知意图下做什么"
    - 不同意图可以接不同工具集 (退款 lab 接退款 API, FAQ lab 接 RAG)

架构:
    user_msg → classify_intent (轻量 LLM 调用)
            → 按意图选 system_prompt + tools
            → create_deep_agent + 调用

Run:
    python 03_intent_with_deepagent.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ===== 意图分类 =====
class Intent(BaseModel):
    category: Literal["faq", "order_query", "refund", "chitchat", "complaint"]
    confidence: float = Field(ge=0.0, le=1.0)


_CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "电商客服意图分类器. 输出意图类别: "
            "faq / order_query / refund / chitchat / complaint",
        ),
        ("human", "{message}"),
    ]
)


def classify(message: str) -> Intent:
    llm = get_llm(temperature=0.0)
    chain = _CLASSIFY_PROMPT | llm.with_structured_output(Intent)
    return chain.invoke({"message": message})


# ===== 不同意图对应的工具 =====
@tool
def query_order(order_id: str) -> str:
    """查询订单状态.

    Args:
        order_id: 订单 ID, 如 O20260427
    """
    return f"订单 {order_id}: 状态=配送中, 预计明日送达, 物流单号 SF1234567"


@tool
def init_refund(order_id: str, reason: str) -> str:
    """发起退款.

    Args:
        order_id: 订单 ID
        reason: 退款原因
    """
    return f"已为订单 {order_id} 发起退款 (原因: {reason}), 工单 RF-{order_id}-A1, 1-3 工作日到账"


@tool
def search_faq(query: str) -> str:
    """检索常见问题知识库.

    Args:
        query: 搜索关键词
    """
    kb = {
        "退货": "退货政策: 商品签收后 7 天无理由退货, 商品需保持原样.",
        "支付": "支付方式: 支付宝、微信、银联、花呗分期.",
        "营业": "营业时间: 客服 7x24 小时在线, 仓库工作日发货.",
        "发票": "发票: 默认电子发票, 需纸质请联系客服.",
    }
    for k, v in kb.items():
        if k in query:
            return v
    return "未在知识库找到相关内容, 建议转人工."


@tool
def escalate_to_human(reason: str) -> str:
    """转人工客服.

    Args:
        reason: 转人工原因
    """
    return f"已转人工客服 (原因: {reason}), 工单 CL-A1, 30 分钟内回复"


# ===== 按意图选 prompt + tools =====
_INTENT_CONFIG: dict = {
    "faq": {
        "system_prompt": "你是 FAQ 客服. 用 search_faq 检索, 简短回答.",
        "tools": [search_faq],
    },
    "order_query": {
        "system_prompt": "你是订单客服. 用 query_order 查订单, 简短报告.",
        "tools": [query_order],
    },
    "refund": {
        "system_prompt": "你是退款客服. 询问/确认订单 ID 和原因后, 用 init_refund 发起退款.",
        "tools": [init_refund, query_order],  # 退款可能需要先查单
    },
    "chitchat": {
        "system_prompt": "你是友好客服, 简短回应闲聊, 不用工具.",
        "tools": [],
    },
    "complaint": {
        "system_prompt": "你是处理投诉的客服, 安抚情绪 + 用 escalate_to_human 转人工.",
        "tools": [escalate_to_human],
    },
}


def chat(user_msg: str) -> dict:
    """带意图识别的对话."""
    intent = classify(user_msg)
    cfg = _INTENT_CONFIG[intent.category]

    print(f"  [意图] {intent.category} (conf={intent.confidence:.2f})")
    print(f"  [系统提示] {cfg['system_prompt'][:60]}...")
    print(f"  [可用工具] {[t.name for t in cfg['tools']]}")

    agent = create_deep_agent(
        model=get_llm(),
        tools=cfg["tools"],
        system_prompt=cfg["system_prompt"],
    )

    result = agent.invoke(
        {"messages": [HumanMessage(content=user_msg)]},
        config={"recursion_limit": 10},
    )
    messages = result["messages"]
    tool_calls_made: list[str] = []
    for m in messages:
        for tc in getattr(m, "tool_calls", []) or []:
            tool_calls_made.append(tc.get("name", ""))

    return {
        "intent": intent.category,
        "tool_calls_made": sorted(set(tool_calls_made)),
        "tool_msgs": sum(1 for m in messages if isinstance(m, ToolMessage)),
        "reply": messages[-1].content,
    }


def main() -> None:
    print("=" * 60)
    print("Ch4.2.2 · 03 DeepAgent + 意图识别前置分流")
    print("=" * 60)

    test_cases = [
        "你们的退货政策是什么?",
        "查一下我的订单 O20260427 物流",
        "我要退款! 订单 O123, 衣服掉色!",
        "你好, 在吗?",
        "等了 5 天还没到, 你们快递太慢了!",
    ]

    for msg in test_cases:
        print(f"\n--- 用户: {msg} ---")
        out = chat(msg)
        print(f"  [结果] intent={out['intent']}, tools_used={out['tool_calls_made']}, "
              f"tool_msgs={out['tool_msgs']}")
        print(f"  [回复] {out['reply'][:200]}")


if __name__ == "__main__":
    main()

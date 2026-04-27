"""01 · 意图分类 — 用 Pydantic Schema 做结构化输出.

LLM 不靠 if-else 判断意图, 而是返回符合 Schema 的对象.

教学要点:
    1. Literal 字段限定意图类别
    2. confidence 字段让 LLM 报告置信度
    3. extracted_entities 字段一次性提取槽位 (类似 NLU 的 slot filling)
    4. with_structured_output 自动校验 + 重试

Run:
    python 01_intent_classify.py
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
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


class Intent(BaseModel):
    """用户意图分类结果."""

    category: Literal["faq", "order_query", "refund", "chitchat", "complaint"] = Field(
        description="意图类别: faq=知识问答, order_query=订单查询, refund=退款, chitchat=闲聊, complaint=投诉"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="置信度 0-1")
    extracted_entities: dict = Field(
        default_factory=dict,
        description="提取的实体, 如 {'order_id': 'O1234', 'product': '羽绒服'}",
    )
    reasoning: str = Field(description="为什么判断成这个类别 (一句话)")


CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是电商客服的意图分类器. 根据用户消息判断意图, 严格按 Schema 输出.\n"
            "类别:\n"
            "  faq         — 一般问题 (退货政策/营业时间/支付方式)\n"
            "  order_query — 查具体订单状态\n"
            "  refund      — 退款诉求 (含申请/进度查询)\n"
            "  chitchat    — 闲聊问候\n"
            "  complaint   — 投诉/吐槽",
        ),
        ("human", "{message}"),
    ]
)


def classify_intent(message: str) -> Intent:
    """对单条用户消息做意图分类."""
    llm = get_llm(temperature=0.0)  # 分类任务温度调到 0 提高一致性
    structured = llm.with_structured_output(Intent)
    chain = CLASSIFY_PROMPT | structured
    return chain.invoke({"message": message})


def main() -> None:
    print("=" * 60)
    print("Ch4.2.2 · 01 意图分类 (Pydantic Schema)")
    print("=" * 60)

    test_cases = [
        "你们的退货政策是什么?",
        "我想查一下订单 O20260427 的物流",
        "我要退款! 那个羽绒服洗了掉色!",
        "你好, 在吗?",
        "你们快递员太慢了, 整整等了 5 天才到!",
        "支付宝可以用吗?",
        "麻烦帮我退掉订单 O123 那件衣服",
    ]

    for msg in test_cases:
        intent = classify_intent(msg)
        emoji = {
            "faq": "❓",
            "order_query": "📦",
            "refund": "💰",
            "chitchat": "💬",
            "complaint": "😡",
        }.get(intent.category, "?")
        print(f"\n用户: {msg}")
        print(
            f"  → {emoji} {intent.category:>12s}  "
            f"conf={intent.confidence:.2f}  "
            f"entities={intent.extracted_entities}"
        )
        print(f"  → reasoning: {intent.reasoning}")


if __name__ == "__main__":
    main()

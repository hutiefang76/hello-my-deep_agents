"""04 · L4 LLM Router — 8 意图分流.

升级理由 (Why upgrade from L3):
    L3 只 1 个 chain 处理 FAQ. 真实业务有 8+ 意图 (faq/order/refund/logistics/...),
    每个意图的 prompt + 工具不同, 全塞一个 chain → prompt 臃肿效果差.
    L4 用 Router: 先判意图, 走对应 sub-chain (各自有专门 prompt + 工具).

Run:
    python 04_l4_router.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from cs_kb import CS_KB, INTENT_CATEGORIES  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


class IntentClassification(BaseModel):
    intent: Literal[
        "faq", "order_query", "refund", "logistics", "payment",
        "complaint", "membership", "chitchat",
    ]
    confidence: float = Field(ge=0.0, le=1.0)


# ============================================================
# 8 个 sub-chain (每意图一个 handler)
# ============================================================


def handle_faq(q: str) -> str:
    llm = get_llm()
    kb_text = "\n".join(f"  - {k}: {v}" for k, v in CS_KB.items())
    prompt = ChatPromptTemplate.from_messages(
        [("system", f"FAQ 客服, 严格基于:\n{kb_text}\n回答 ≤ 80 字."), ("human", "{q}")]
    )
    return (prompt | llm | StrOutputParser()).invoke({"q": q})


def handle_order_query(q: str) -> str:
    # 真实场景调订单 API, 这里 mock
    return "[订单查询] 订单 O20260427: 状态=配送中, 顺丰单号 SF1234567, 预计明天送达."


def handle_refund(q: str) -> str:
    return "[退款流程] 已为您发起退款工单 RF-A1, 7 个工作日内审核通过后 1-3 天到账."


def handle_logistics(q: str) -> str:
    return "[物流] 订单 O20260427 当前已到上海中转, 预计明日 18:00 前送达."


def handle_payment(q: str) -> str:
    llm = get_llm()
    return llm.invoke(
        f"用户支付问题: {q}. 简短回答 ≤ 60 字, 引导到对应支付方式或客户经理."
    ).content


def handle_complaint(q: str) -> str:
    return "[投诉] 已记录您的投诉, 工单号 CL-A1, 24 小时内主管会回访您."


def handle_membership(q: str) -> str:
    llm = get_llm()
    membership_kb = "\n".join(f"  - {k}: {v}" for k, v in CS_KB.items() if "会员" in k or "卡" in k)
    return llm.invoke(
        f"会员问题: {q}\n\n会员 KB:\n{membership_kb}\n\n简短回答 ≤ 60 字."
    ).content


def handle_chitchat(q: str) -> str:
    llm = get_llm()
    return llm.invoke(f"作为客服, 简短友好回应闲聊: {q}").content


_HANDLERS = {
    "faq": handle_faq,
    "order_query": handle_order_query,
    "refund": handle_refund,
    "logistics": handle_logistics,
    "payment": handle_payment,
    "complaint": handle_complaint,
    "membership": handle_membership,
    "chitchat": handle_chitchat,
}


# ============================================================
# Router 主入口
# ============================================================


_classify_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "电商客服意图分类器. 类别: faq/order_query/refund/logistics/payment/"
            "complaint/membership/chitchat",
        ),
        ("human", "{q}"),
    ]
)


def l4_handle(query: str) -> dict:
    """L4 Router: classify → route."""
    llm = get_llm(temperature=0.0)
    t0 = time.perf_counter()

    classification: IntentClassification = (
        _classify_prompt | llm.with_structured_output(IntentClassification)
    ).invoke({"q": query})

    handler = _HANDLERS[classification.intent]
    answer = handler(query)

    return {
        "level": "L4",
        "intent": classification.intent,
        "confidence": classification.confidence,
        "answer": answer,
        "ms": (time.perf_counter() - t0) * 1000,
        "cost": 0.005,
    }


def main() -> None:
    print("=" * 70)
    print("Ch9 · 04 L4 LLM Router — 8 意图分流")
    print("=" * 70)

    queries = [
        ("我那双鞋开胶了急用!", "faq/refund?"),
        ("查我订单 O20260427", "order_query"),
        ("我要退款", "refund"),
        ("快递到哪了", "logistics"),
        ("花呗能用吗", "payment"),
        ("等了 5 天还没到!!!", "complaint"),
        ("钻石会员折扣几折", "membership"),
        ("你好啊~", "chitchat"),
    ]

    for q, expected in queries:
        result = l4_handle(q)
        match = "✅" if expected in result["intent"] or result["intent"] in expected else "?"
        print(f"\n  {match} Q: {q[:40]:<40} (expected: {expected})")
        print(f"     intent: {result['intent']} (conf={result['confidence']:.2f})")
        print(f"     A: {result['answer'][:100]}")
        print(f"     {result['ms']:.0f}ms, ~¥{result['cost']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 8 意图各走专门 handler, 每个 handler 有自己的 prompt + 数据/工具")
    print("  - 路由分类成本低 (单次 LLM, 几百 tokens)")
    print("  - 但 L4 仍是 workflow — 不能处理 '查单+改单+发券' 这类多步任务")
    print("  - 升级到 L5 Agent (DeepAgent + Tools + Reflection)")


if __name__ == "__main__":
    main()

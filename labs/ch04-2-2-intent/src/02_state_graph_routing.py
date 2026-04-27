"""02 · LangGraph StateGraph 条件路由.

把上一节的意图分类接进 LangGraph, 不同意图走不同 handler 节点.

类比 Spring StateMachine:
    @WithStateMachine                    StateGraph(GraphState)
    states: { faq, order, refund, ... }  add_node("handle_faq", ...) ...
    transitions: from S1 to S2 if event  add_conditional_edges(...)

教学要点:
    1. TypedDict 定义状态
    2. classify 节点写 intent 到 state
    3. add_conditional_edges 按 intent 跳不同节点
    4. 每个 handler 节点是独立函数, 单一职责

Run:
    python 02_state_graph_routing.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, TypedDict

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ===== 1. 意图 Schema (复用上节) =====
class Intent(BaseModel):
    category: Literal["faq", "order_query", "refund", "chitchat", "complaint"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


# ===== 2. 图状态 =====
class GraphState(TypedDict):
    user_msg: str
    intent: str          # classify 节点写
    confidence: float
    response: str        # handler 节点写


# ===== 3. 节点: 分类 =====
CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "电商客服意图分类器. 类别: faq / order_query / refund / chitchat / complaint",
        ),
        ("human", "{message}"),
    ]
)


def classify_node(state: GraphState) -> dict:
    llm = get_llm(temperature=0.0)
    structured = llm.with_structured_output(Intent)
    chain = CLASSIFY_PROMPT | structured
    intent = chain.invoke({"message": state["user_msg"]})
    print(f"  [classify] {state['user_msg'][:40]}... → {intent.category} ({intent.confidence:.2f})")
    return {"intent": intent.category, "confidence": intent.confidence}


# ===== 4. 节点: 各意图 handler (单一职责) =====
def handle_faq(state: GraphState) -> dict:
    """FAQ — 走 RAG 检索 (本 lab 简化为静态回答)."""
    response = "[FAQ] 退货政策: 7 天无理由; 营业: 全天 24h; 支付: 支付宝/微信/银联."
    print(f"  [handle_faq] 简化回答")
    return {"response": response}


def handle_order(state: GraphState) -> dict:
    """订单查询 — 应该调订单 API, 这里 mock."""
    response = "[订单查询] 已查到订单 O20260427: 状态=配送中, 预计明日送达."
    print(f"  [handle_order] mock 订单 API")
    return {"response": response}


def handle_refund(state: GraphState) -> dict:
    """退款 — 应该走退款流程, 这里 mock."""
    response = "[退款] 已为您发起退款工单 RF-20260427-A1, 1-3 个工作日到账."
    print(f"  [handle_refund] mock 退款流程")
    return {"response": response}


def handle_chitchat(state: GraphState) -> dict:
    """闲聊 — 直接调 LLM 走轻量回复."""
    llm = get_llm()
    resp = llm.invoke(f"作为客服, 简短回应这条闲聊: {state['user_msg']}")
    print(f"  [handle_chitchat] LLM 直答")
    return {"response": f"[闲聊] {resp.content}"}


def handle_complaint(state: GraphState) -> dict:
    """投诉 — 应该转人工, 这里 mock."""
    response = "[投诉] 已为您转接人工客服, 工单号 CL-20260427-X9, 30 分钟内回复."
    print(f"  [handle_complaint] 转人工")
    return {"response": response}


# ===== 5. 路由函数 =====
def route_by_intent(state: GraphState) -> str:
    return state["intent"]


# ===== 6. 构图 =====
def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("classify", classify_node)
    workflow.add_node("handle_faq", handle_faq)
    workflow.add_node("handle_order", handle_order)
    workflow.add_node("handle_refund", handle_refund)
    workflow.add_node("handle_chitchat", handle_chitchat)
    workflow.add_node("handle_complaint", handle_complaint)

    workflow.add_edge(START, "classify")
    workflow.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "faq": "handle_faq",
            "order_query": "handle_order",
            "refund": "handle_refund",
            "chitchat": "handle_chitchat",
            "complaint": "handle_complaint",
        },
    )
    for node in ["handle_faq", "handle_order", "handle_refund", "handle_chitchat", "handle_complaint"]:
        workflow.add_edge(node, END)

    return workflow.compile()


def main() -> None:
    print("=" * 60)
    print("Ch4.2.2 · 02 LangGraph StateGraph 路由")
    print("=" * 60)
    graph = build_graph()

    test_cases = [
        "你们退货政策是什么?",
        "我要查订单 O20260427",
        "申请退款!",
        "你好啊~",
        "快递员太慢了我要投诉!",
    ]

    for msg in test_cases:
        print(f"\n--- 用户: {msg} ---")
        result = graph.invoke({"user_msg": msg, "intent": "", "confidence": 0.0, "response": ""})
        print(f"最终回复: {result['response']}")


if __name__ == "__main__":
    main()

"""05 · L5 Autonomous Agent — DeepAgent + Tools + Reflection.

升级理由 (Why upgrade from L4):
    L4 处理"单一意图"很好, 但用户说"查我订单 O123 物流, 然后退款 100, 顺便发个 50 元券"
    → 3 个动作, L4 router 只能选一个 handler.
    L5 用 DeepAgent: LLM 自己决定调几个工具 + 顺序 + 何时反思 + 何时停.

Run:
    python 05_l5_autonomous_agent.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from cs_kb import CS_KB  # noqa: E402
from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# ============================================================
# Tools (mock 业务 API)
# ============================================================


@tool
def query_order(order_id: str) -> str:
    """查询订单详情.

    Args:
        order_id: 订单 ID
    """
    fake_db = {
        "O20260427": "状态=配送中, 商品=羽绒服, 金额=¥599, 顺丰 SF1234567, ETA 明日",
        "O20260428": "状态=已签收, 商品=运动鞋, 金额=¥399, 京东 JD7777",
    }
    return fake_db.get(order_id, f"Order {order_id} not found")


@tool
def issue_refund(order_id: str, amount: float, reason: str) -> str:
    """发起退款.

    Args:
        order_id: 订单 ID
        amount: 金额 (≥0)
        reason: 原因
    """
    return f"已为 {order_id} 发起退款 ¥{amount} (原因: {reason}), 工单 RF-A1, 1-3 工作日到账."


@tool
def issue_coupon(user_id: str, amount: float, reason: str) -> str:
    """发优惠券.

    Args:
        user_id: 用户 ID
        amount: 面额
        reason: 原因
    """
    return f"已为 {user_id} 发放 ¥{amount} 优惠券 (原因: {reason}), 7 天有效."


@tool
def search_kb(query: str) -> str:
    """检索内部 FAQ 知识库.

    Args:
        query: 关键词
    """
    for k, v in CS_KB.items():
        if k in query or query in k:
            return f"[{k}] {v}"
    return "未找到相关 FAQ"


@tool
def escalate_to_human(reason: str) -> str:
    """转人工客服.

    Args:
        reason: 转人工原因
    """
    return f"已转人工客服 (原因: {reason}), 工单 CL-A1, 30 分钟内回复."


# ============================================================
# L5 Agent (DeepAgent + 全工具 + 业务红线)
# ============================================================


SYSTEM_PROMPT = """你是电商客服资深 Agent. 你能调以下工具:
  - query_order      查订单
  - issue_refund     退款
  - issue_coupon     发券
  - search_kb        查 FAQ
  - escalate_to_human 转人工

工作流程:
  1. 用 write_todos 列计划 (3-5 步)
  2. 按计划调工具 (可多个并行)
  3. 用 write_file 把"工单总结"写到 'ticket.md'
  4. 给用户简短确认

业务红线 (绝不能违反):
  - 退款金额必须 ≤ 订单金额
  - 优惠券面额 ≤ ¥100 (单次)
  - P0 工单 (人身/法律) 必须转人工
  - 不得使用"保证/绝对/100%"等敏感承诺词"""


def l5_handle(query: str) -> dict:
    agent = create_deep_agent(
        model=get_llm(),
        tools=[query_order, issue_refund, issue_coupon, search_kb, escalate_to_human],
        system_prompt=SYSTEM_PROMPT,
    )

    t0 = time.perf_counter()
    result = agent.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"recursion_limit": 30},
    )
    elapsed = (time.perf_counter() - t0) * 1000

    msgs = result["messages"]
    files = result.get("files", {})
    todos = result.get("todos", [])

    tools_used: list[str] = []
    for m in msgs:
        for tc in getattr(m, "tool_calls", []) or []:
            tools_used.append(tc.get("name", ""))

    return {
        "level": "L5",
        "answer": msgs[-1].content,
        "tools_used": tools_used,
        "tool_call_count": sum(1 for m in msgs if isinstance(m, ToolMessage)),
        "files_created": list(files.keys()),
        "todos": [t.get("content", "") for t in todos],
        "ms": elapsed,
        "cost": 0.020 + 0.005 * len(tools_used),  # 估算
    }


def main() -> None:
    print("=" * 70)
    print("Ch9 · 05 L5 Autonomous Agent — DeepAgent + Tools + Planning")
    print("=" * 70)

    queries = [
        # 简单 query (用 L5 是浪费, 但展示能处理)
        "退货政策什么样?",

        # L4 也能处理的单一意图
        "查我订单 O20260427",

        # L4 处理不了的多步任务 — L5 真正闪光的地方
        (
            "我订单 O20260427 鞋子开胶, 帮我:"
            "1. 查一下订单状态 "
            "2. 退款 ¥599 "
            "3. 给我发个 50 元的优惠券补偿 "
            "顺便告诉我退货政策"
        ),
    ]

    for q in queries:
        print(f"\n--- Q: {q[:80]}... ---")
        result = l5_handle(q)
        print(f"  tools_used: {result['tools_used']}")
        print(f"  files: {result['files_created']}, todos: {len(result['todos'])} 条")
        print(f"  A: {result['answer'][:200]}")
        print(f"  {result['ms']:.0f}ms, ~¥{result['cost']:.3f}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - L5 真正闪光: '查单+退款+发券+查 FAQ' 单次 query 自主完成")
    print("  - 简单 query 用 L5 = 浪费 (该降级到 L1/L2)")
    print("  - 这就是 Chase 强调的 cognitive architecture: 你的'决策树' 选哪级")
    print("  - 业务红线在 system_prompt 里 (Own this), DeepAgent 框架是 Outsource")


if __name__ == "__main__":
    main()

"""01 · Tool Engineering — 生产级工具四件套.

OpenAI Practical Guide #1: "Tools are APIs: validate inputs/outputs, make side
effects idempotent, and budget time/cost."

四件套 (Four Disciplines):
    1. Contract (契约): Pydantic args/return + clear docstring
    2. Idempotency (幂等): 同参数多次调用结果一致, 不重复扣款/发货
    3. Timeout (超时): 工具不能无限等, 必须设上限
    4. Circuit Breaker (熔断): 连续失败后跳闸, 避免雪崩

Run:
    python 01_tool_engineering.py
"""

from __future__ import annotations

import functools
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ============================================================
# Pillar 1: Contract — Pydantic args + return type
# ============================================================


class RefundArgs(BaseModel):
    """退款工具入参 (严格契约)."""

    order_id: str = Field(min_length=3, max_length=32, description="订单 ID, 如 O20260427")
    amount: float = Field(gt=0, description="退款金额, 必须 > 0")
    reason: str = Field(min_length=1, max_length=500, description="退款原因")
    idempotency_key: str = Field(description="幂等键 (UUID), 同 key 多次调用结果一致")


class RefundResult(BaseModel):
    """退款工具返回 (严格契约)."""

    refund_id: str
    status: str  # "success" | "duplicate" | "failed"
    message: str


# ============================================================
# Pillar 2: Idempotency — 同 key 不重复执行
# ============================================================


@dataclass
class IdempotencyStore:
    """幂等存储 — 真实场景用 Redis, 这里用内存 dict."""

    cache: dict[str, RefundResult] = field(default_factory=dict)


_IDEMP = IdempotencyStore()
_REFUND_DB: dict[str, dict] = {}  # mock 退款数据库


# ============================================================
# Pillar 3: Timeout — 装饰器
# ============================================================


def with_timeout(seconds: float):
    """超时装饰器 (简化版, 真实生产用 asyncio.wait_for)."""

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = time.perf_counter() - t0
            if elapsed > seconds:
                raise TimeoutError(f"Tool {fn.__name__} took {elapsed:.2f}s > {seconds}s")
            return result

        return wrapper

    return deco


# ============================================================
# Pillar 4: Circuit Breaker — 连续失败跳闸
# ============================================================


@dataclass
class CircuitBreaker:
    """熔断器 — 连续失败 N 次后 OPEN, 不再放请求过去."""

    failure_threshold: int = 3
    cooldown_sec: float = 30.0
    state: str = "closed"  # closed | open | half_open
    failure_count: int = 0
    last_fail_time: float = 0

    def can_call(self) -> tuple[bool, str]:
        if self.state == "open":
            if time.time() - self.last_fail_time > self.cooldown_sec:
                self.state = "half_open"
                return True, "circuit half_open, trying"
            return False, f"circuit OPEN (cooldown {self.cooldown_sec}s)"
        return True, "circuit closed"

    def on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self):
        self.failure_count += 1
        self.last_fail_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


_REFUND_BREAKER = CircuitBreaker(failure_threshold=3)


# ============================================================
# 集大成: 退款工具 (4 Pillar 全用上)
# ============================================================


@tool(args_schema=RefundArgs)
@with_timeout(seconds=5.0)
def issue_refund(
    order_id: str, amount: float, reason: str, idempotency_key: str
) -> dict:
    """对订单发起退款 (生产级实现, 4 Pillar 全用).

    Returns dict matching RefundResult schema.
    """
    # === Pillar 4: Circuit Breaker 检查 ===
    can_call, msg = _REFUND_BREAKER.can_call()
    if not can_call:
        return {"refund_id": "", "status": "failed", "message": msg}

    # === Pillar 2: 幂等性检查 (同 key 直接返回缓存) ===
    if idempotency_key in _IDEMP.cache:
        cached = _IDEMP.cache[idempotency_key]
        return {**cached.model_dump(), "status": "duplicate"}

    # === Pillar 1: Contract (Pydantic 已校验入参) ===

    # 业务逻辑: mock DB 写入
    if order_id not in _REFUND_DB:
        _REFUND_BREAKER.on_failure()
        return {
            "refund_id": "",
            "status": "failed",
            "message": f"Order {order_id} not found",
        }

    refund_id = f"RF-{order_id}-{uuid.uuid4().hex[:8]}"
    _REFUND_DB[order_id]["refund"] = {
        "refund_id": refund_id,
        "amount": amount,
        "reason": reason,
    }

    result = RefundResult(
        refund_id=refund_id,
        status="success",
        message=f"Refund {amount} for {order_id} processed",
    )

    # === Pillar 2: 写入幂等缓存 ===
    _IDEMP.cache[idempotency_key] = result

    # === Pillar 4: 成功重置熔断 ===
    _REFUND_BREAKER.on_success()

    return result.model_dump()


def main() -> None:
    print("=" * 70)
    print("Ch8 · 01 Tool Engineering — 4 Pillars (Contract/Idemp/Timeout/CB)")
    print("=" * 70)

    # 准备 mock 数据
    _REFUND_DB["O20260427"] = {"amount": 599.0, "status": "shipped"}
    _REFUND_DB["O20260428"] = {"amount": 199.0, "status": "shipped"}

    # ===== 1. 直接调用工具 (展示契约 + 幂等) =====
    print("\n--- 1. Contract + Idempotency ---")
    idem_key = str(uuid.uuid4())

    print(f"调用 1 次 (key={idem_key[:8]}...):")
    r1 = issue_refund.invoke(
        {
            "order_id": "O20260427",
            "amount": 599.0,
            "reason": "客户投诉掉色",
            "idempotency_key": idem_key,
        }
    )
    print(f"  result: {r1}")

    print(f"\n调用 2 次 (同 key, 应返回 duplicate):")
    r2 = issue_refund.invoke(
        {
            "order_id": "O20260427",
            "amount": 599.0,
            "reason": "客户投诉掉色",
            "idempotency_key": idem_key,
        }
    )
    print(f"  result: {r2}")
    assert r2["status"] == "duplicate", f"幂等失败! got {r2['status']}"
    print("  ✅ 幂等检查通过 (duplicate)")

    # ===== 2. 失败 → Circuit Breaker 跳闸 =====
    print("\n--- 2. Circuit Breaker ---")
    print(f"故意调 4 次不存在的订单, 触发熔断 (threshold=3):")
    for i in range(4):
        r = issue_refund.invoke(
            {
                "order_id": f"NOT-EXIST-{i}",
                "amount": 100.0,
                "reason": "test",
                "idempotency_key": f"k-{i}",
            }
        )
        print(f"  attempt {i+1}: status={r['status']}, msg={r['message'][:60]}")

    # ===== 3. LLM 调用此工具 =====
    print("\n--- 3. LLM 通过 bind_tools 调用 (展示真实 Agent 路径) ---")
    # 重置熔断让 LLM 测试
    _REFUND_BREAKER.state = "closed"
    _REFUND_BREAKER.failure_count = 0

    llm = get_llm().bind_tools([issue_refund])
    response = llm.invoke(
        [
            HumanMessage(
                content=(
                    "客户订单 O20260428 商品有质量问题, 金额 199 元, "
                    "请发起退款 (用 idempotency_key='user-req-001')"
                )
            )
        ]
    )
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"  LLM 调 {tc['name']}({tc['args']})")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - Pydantic args_schema 让 LLM 不能传错参数 (校验前置)")
    print("  - Idempotency Key 让重复调用安全 (用户重试不会重复扣款)")
    print("  - Circuit Breaker 防雪崩 (下游崩了不让 LLM 一直试)")
    print("  - Timeout 防 LLM 无限等待挂起 Agent")
    print("=" * 70)


if __name__ == "__main__":
    main()

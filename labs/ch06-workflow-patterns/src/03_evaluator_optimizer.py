"""03 · Evaluator-Optimizer — 评估-优化循环.

Anthropic Pattern #5.

定义 (Definition):
    Generator LLM produces output, Evaluator LLM critiques. Loop until pass criteria.
    生成器 LLM 出结果, 评估器 LLM 挑错, 循环直到满足标准.

何时用 (When):
    - 评估标准清晰 (e.g. "代码必须通过单测", "文案不能含敏感词")
    - 迭代精炼有可衡量价值 (不是越改越烂)
    - 单次 prompt 难一次写对的复杂任务

vs Reflection (Andrew Ng 模式):
    - Reflection: 同一个 LLM 自评自改 (Self-Critique)
    - Evaluator-Optimizer: **不同 prompt 的 LLM 角色分离** (Generator vs Evaluator),
                           Evaluator 通常用更严格的 system prompt

双业务 (Dual Business):
    主 客服: 回复质量 → 评估 (语气/信息完整/合规) → 改 → 直到通过
    对照 数分: SQL 生成 → 跑 → 看错 → 改 → 跑 → 直到正确

Run:
    python 03_evaluator_optimizer.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ============================================================
# 主业务: 客服回复质量循环
# ============================================================


class CSReplyEval(BaseModel):
    """评估器输出."""

    pass_check: bool = Field(description="是否通过质量标准")
    score: int = Field(ge=0, le=100, description="质量分 0-100")
    issues: list[str] = Field(description="具体问题列表")
    suggestions: list[str] = Field(description="改进建议")


def cs_evaluator_optimizer(complaint: str, max_rounds: int = 3) -> dict:
    """客服回复 Evaluator-Optimizer 循环."""
    llm = get_llm()

    # ===== Generator =====
    gen_prompt = ChatPromptTemplate.from_template(
        "You are a customer service rep. Reply to this complaint in 80 字以内.\n"
        "Complaint: {complaint}\n"
        "Previous attempt issues (if any): {prev_issues}"
    )

    # ===== Evaluator =====
    eval_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a STRICT customer service quality auditor. Check the reply against:\n"
                "  1. Empathy (含共情语句, 不冷漠)\n"
                "  2. Action (明确给出下一步行动)\n"
                "  3. Compliance (无 '保证/绝对/100%/终身' 这类承诺)\n"
                "  4. Length (≤ 80 字)\n"
                "  5. Tone (不卑不亢, 不过度道歉)\n\n"
                "Strict mode: only pass if all 5 are met.",
            ),
            ("human", "Complaint: {complaint}\n\nReply: {reply}\n\nEvaluate strictly."),
        ]
    )

    prev_issues = "(none, first attempt)"
    history: list[dict] = []

    for round_no in range(1, max_rounds + 1):
        print(f"\n  --- Round {round_no} ---")

        # Generate
        reply = (gen_prompt | llm | StrOutputParser()).invoke(
            {"complaint": complaint, "prev_issues": prev_issues}
        )
        print(f"  [Gen]   {reply[:80]}...")

        # Evaluate (用更严格的 LLM 设置)
        evaluator = get_llm(temperature=0.0)
        eval_result: CSReplyEval = (
            eval_prompt | evaluator.with_structured_output(CSReplyEval)
        ).invoke({"complaint": complaint, "reply": reply})
        print(f"  [Eval]  pass={eval_result.pass_check}, score={eval_result.score}")
        if eval_result.issues:
            print(f"          issues={eval_result.issues}")

        history.append(
            {
                "round": round_no,
                "reply": reply,
                "pass": eval_result.pass_check,
                "score": eval_result.score,
                "issues": eval_result.issues,
            }
        )

        if eval_result.pass_check:
            print(f"  ✅ Round {round_no} 通过, 退出循环")
            return {"final_reply": reply, "rounds": round_no, "history": history}

        # 把 issues 塞给下一轮 generator
        prev_issues = "; ".join(eval_result.issues + eval_result.suggestions)

    # 用完 max_rounds 还没通过
    return {
        "final_reply": history[-1]["reply"],
        "rounds": max_rounds,
        "history": history,
        "max_rounds_hit": True,
    }


# ============================================================
# 对照业务: SQL 生成-执行-纠错循环
# ============================================================


# 模拟数据库 (in-memory)
_FAKE_DB = {
    "products": [
        {"id": 1, "name": "iPhone", "price": 999, "category": "electronics"},
        {"id": 2, "name": "Jeans", "price": 99, "category": "clothing"},
        {"id": 3, "name": "Coffee", "price": 5, "category": "food"},
    ],
    "orders": [
        {"id": "O1", "product_id": 1, "qty": 2, "amount": 1998},
        {"id": "O2", "product_id": 2, "qty": 1, "amount": 99},
        {"id": "O3", "product_id": 1, "qty": 1, "amount": 999},
    ],
}


def fake_sql_executor(query: str) -> dict:
    """假 SQL 执行器 — 只支持极简 SELECT, 否则返回错误."""
    query_lower = query.lower().strip()

    # 极度简化的 "SQL parser"
    if "from products" in query_lower and "select" in query_lower:
        if "category" in query_lower and "electronics" in query_lower:
            rows = [p for p in _FAKE_DB["products"] if p["category"] == "electronics"]
            return {"ok": True, "rows": rows, "count": len(rows)}
        return {"ok": True, "rows": _FAKE_DB["products"], "count": 3}

    if "from orders" in query_lower:
        if "sum" in query_lower:
            total = sum(o["amount"] for o in _FAKE_DB["orders"])
            return {"ok": True, "rows": [{"total": total}], "count": 1}
        return {"ok": True, "rows": _FAKE_DB["orders"], "count": 3}

    return {"ok": False, "error": f"Syntax error or unsupported: {query[:80]}"}


def da_evaluator_optimizer(question: str, max_rounds: int = 3) -> dict:
    """数据分析师 SQL 生成-执行-纠错."""
    llm = get_llm()

    gen_prompt = ChatPromptTemplate.from_template(
        "You are SQL Generator. Tables: products(id,name,price,category), "
        "orders(id,product_id,qty,amount). Write ONE SQL query (no explanation) for:\n"
        "Question: {q}\n\n"
        "Previous error (if any): {prev_error}"
    )

    prev_error = "(none, first attempt)"
    history: list[dict] = []

    for round_no in range(1, max_rounds + 1):
        print(f"\n  --- Round {round_no} ---")

        sql_raw = (gen_prompt | llm | StrOutputParser()).invoke(
            {"q": question, "prev_error": prev_error}
        )

        # 提取 SQL (LLM 可能包了 ```sql```)
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", sql_raw, re.DOTALL)
        sql = match.group(1).strip() if match else sql_raw.strip()
        print(f"  [Gen]   SQL: {sql[:100]}...")

        # Execute (这就是 evaluator — 真实数据库执行结果就是评判)
        exec_result = fake_sql_executor(sql)
        print(f"  [Exec]  ok={exec_result['ok']}")

        history.append(
            {"round": round_no, "sql": sql, "exec": exec_result}
        )

        if exec_result["ok"]:
            print(f"  ✅ Round {round_no} 执行成功, 退出循环")
            return {
                "final_sql": sql,
                "rows": exec_result["rows"],
                "rounds": round_no,
                "history": history,
            }

        # 把执行错误塞给下一轮 generator
        prev_error = exec_result["error"]
        print(f"  [Err]   {prev_error}")

    return {
        "rounds": max_rounds,
        "history": history,
        "max_rounds_hit": True,
        "last_error": prev_error,
    }


def main() -> None:
    print("=" * 70)
    print("Ch6 · 03 Evaluator-Optimizer (评估-优化循环) — Anthropic Pattern #5")
    print("=" * 70)

    # ===== 主业务 =====
    print("\n--- [主业务] 客服回复质量循环 ---")
    complaint = (
        "我买的鞋子穿了一周就开胶了！我要求 100% 全额退款 + 双倍赔偿!"
    )
    print(f"投诉: {complaint}")
    result = cs_evaluator_optimizer(complaint, max_rounds=3)
    print(f"\n  最终回复: {result['final_reply']}")
    print(f"  迭代轮数: {result['rounds']}")

    # ===== 对照业务 =====
    print("\n\n--- [对照业务] 数据分析 SQL 生成-执行-纠错 ---")
    question = "查电子类目所有产品"
    print(f"问题: {question}")
    result = da_evaluator_optimizer(question, max_rounds=3)
    if result.get("rows"):
        print(f"\n  最终 SQL: {result['final_sql']}")
        print(f"  结果行数: {len(result['rows'])}")
        for r in result["rows"]:
            print(f"    {r}")
    print(f"  迭代轮数: {result['rounds']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - Generator + Evaluator 角色分离, 评估器用严格 system prompt")
    print("  - 失败时把 issues 塞回 Generator 让它针对性改 (closed-loop)")
    print("  - 数据库执行结果天然就是 Evaluator (无需 LLM 评估)")
    print("  - 设 max_rounds 防死循环 (3-5 轮通常够)")
    print("=" * 70)


if __name__ == "__main__":
    main()

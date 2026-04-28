"""01 · Prompt Chaining — 提示词串联.

Anthropic Pattern #1.

定义 (Definition):
    Decompose a task into a sequence of LLM steps, where each step processes the
    output of the previous one. Add programmatic checks ("gate") on intermediate steps.

    中文: 把任务拆成多个 LLM 步骤, 每步处理上步输出. 中间加程序化校验 ("gate").

何时用 (When to use):
    - 任务可清晰拆为 2-5 个线性步骤
    - 中间步骤需要校验 (例: 生成大纲后人工审批再写正文)
    - 单次 prompt 太复杂导致 LLM 出错率高

双业务实战 (Dual Business):
    主业务 客服: 投诉解析 → 严重度分类 → 回复生成 → 敏感词 gate
    对照 数分:   数据脱敏 → 统计计算 → 可视化代码生成

Run:
    python 01_prompt_chaining.py
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
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# ============================================================
# 主业务: 电商客服投诉处理 (Customer Service Complaint Handling)
# Chain: 解析 → 分类 (severity) → 生成回复 → 敏感词 gate
# ============================================================


class ComplaintAnalysis(BaseModel):
    """投诉分析结构 (step 1 输出)."""

    summary: str = Field(description="一句话总结投诉核心")
    products_mentioned: list[str] = Field(description="提到的产品")
    user_emotion: Literal["angry", "frustrated", "neutral", "polite"]


class SeverityLevel(BaseModel):
    """严重度分级 (step 2 输出)."""

    severity: Literal["P0_critical", "P1_high", "P2_medium", "P3_low"] = Field(
        description="P0=危及人身/法律风险, P1=金额>1000元, P2=金额<1000, P3=轻微抱怨"
    )
    needs_human: bool = Field(description="是否需要人工介入")
    reason: str


def gate_check_sensitive_words(reply: str) -> tuple[bool, str]:
    """程序化 gate — 检查回复是否包含敏感词 (不需要 LLM)."""
    forbidden = ["保证", "绝对", "100%", "无条件赔偿", "终身"]
    for word in forbidden:
        if word in reply:
            return False, f"敏感词命中: '{word}' (法务红线, 客服不得使用)"
    return True, "通过"


def cs_chain(complaint: str) -> dict:
    """电商客服 Prompt Chaining."""
    llm = get_llm(temperature=0.0)

    # ===== Step 1: 投诉解析 =====
    step1_prompt = ChatPromptTemplate.from_template(
        "Analyze this customer complaint, output structured.\n\nComplaint: {complaint}"
    )
    analysis: ComplaintAnalysis = (
        step1_prompt | llm.with_structured_output(ComplaintAnalysis)
    ).invoke({"complaint": complaint})
    print(f"  Step 1 解析: {analysis.summary[:60]}... (情绪={analysis.user_emotion})")

    # ===== Step 2: 严重度分类 =====
    step2_prompt = ChatPromptTemplate.from_template(
        "Given the complaint analysis, classify severity:\n"
        "summary={summary}\nproducts={products}\nemotion={emotion}"
    )
    severity: SeverityLevel = (
        step2_prompt | llm.with_structured_output(SeverityLevel)
    ).invoke(
        {
            "summary": analysis.summary,
            "products": analysis.products_mentioned,
            "emotion": analysis.user_emotion,
        }
    )
    print(f"  Step 2 分级: {severity.severity}, 需人工={severity.needs_human}")

    # ===== Gate 1 (程序化): P0 直接转人工, 不让 LLM 写回复 =====
    if severity.severity == "P0_critical":
        return {
            "analysis": analysis.model_dump(),
            "severity": severity.model_dump(),
            "reply": "[已转人工] P0 危急工单, 客服主管 5 分钟内介入",
            "skipped": "LLM 不生成回复 (gate 拦截)",
        }

    # ===== Step 3: 生成回复 =====
    step3_prompt = ChatPromptTemplate.from_template(
        "Write a customer service reply (≤80 字, 中文):\n"
        "summary={summary}\nseverity={severity}\nemotion={emotion}\n"
        "Tone: empathetic but factual. Don't promise unrealistic things."
    )
    reply = (step3_prompt | llm | StrOutputParser()).invoke(
        {
            "summary": analysis.summary,
            "severity": severity.severity,
            "emotion": analysis.user_emotion,
        }
    )
    print(f"  Step 3 回复: {reply[:60]}...")

    # ===== Gate 2 (程序化): 敏感词检查 =====
    passed, gate_msg = gate_check_sensitive_words(reply)
    print(f"  Gate 敏感词: {gate_msg}")

    if not passed:
        # 失败重试: 给 LLM 看 gate 错误信息让它改
        retry_prompt = ChatPromptTemplate.from_template(
            "Rewrite the reply to remove forbidden words. "
            "Forbidden: 保证/绝对/100%/无条件赔偿/终身.\n\n"
            "Original reply: {reply}\nIssue: {issue}"
        )
        reply = (retry_prompt | llm | StrOutputParser()).invoke(
            {"reply": reply, "issue": gate_msg}
        )
        print(f"  Step 3-retry: {reply[:60]}...")

    return {
        "analysis": analysis.model_dump(),
        "severity": severity.model_dump(),
        "reply": reply,
        "gate_passed": passed,
    }


# ============================================================
# 对照业务: 数据分析师助手 (Data Analyst)
# Chain: 数据脱敏 → 统计计算 → 可视化代码
# ============================================================


def da_chain(raw_data: str, question: str) -> dict:
    """数据分析师 Prompt Chaining."""
    llm = get_llm(temperature=0.0)

    # ===== Step 1: 脱敏 =====
    step1 = ChatPromptTemplate.from_template(
        "Sanitize this data — replace PII (names/phones/IDs) with placeholders. "
        "Output only sanitized data.\n\nData:\n{data}"
    )
    sanitized = (step1 | llm | StrOutputParser()).invoke({"data": raw_data})
    print(f"  Step 1 脱敏: {sanitized[:80]}...")

    # ===== Gate (程序化): 检查是否还有手机号 =====
    import re

    if re.search(r"\b\d{11}\b", sanitized):
        return {"error": "Gate 拦截: 仍含 11 位数字, 疑似手机号未脱敏"}

    # ===== Step 2: 统计 =====
    step2 = ChatPromptTemplate.from_template(
        "Given sanitized data and question, compute basic statistics in 50 字以内.\n"
        "Data:\n{data}\n\nQuestion: {q}"
    )
    stats = (step2 | llm | StrOutputParser()).invoke({"data": sanitized, "q": question})
    print(f"  Step 2 统计: {stats[:80]}...")

    # ===== Step 3: 可视化代码 =====
    step3 = ChatPromptTemplate.from_template(
        "Based on stats, write a 5-line matplotlib snippet. Code only, no explanation.\n"
        "Stats: {stats}"
    )
    code = (step3 | llm | StrOutputParser()).invoke({"stats": stats})
    print(f"  Step 3 代码: {code[:80]}...")

    return {"sanitized": sanitized, "stats": stats, "code": code}


def main() -> None:
    print("=" * 70)
    print("Ch6 · 01 Prompt Chaining (提示词串联) — Anthropic Pattern #1")
    print("=" * 70)

    # ===== 主业务 =====
    print("\n--- [主业务] 电商客服投诉处理 ---")
    complaint = (
        "你好我下周一参加婚礼急用！我上周买的羽绒服 (订单 O20260427) 洗了第一次就严重掉色，"
        "今天试穿发现内衬还破了个洞！我要求全额退款 + 赔偿误工费！再不处理我就投诉到 12315!"
    )
    print(f"投诉: {complaint[:100]}...\n")
    result = cs_chain(complaint)
    print(f"\n  最终回复: {result['reply']}")

    # ===== 对照业务 =====
    print("\n--- [对照业务] 数据分析师 (脱敏→统计→可视化) ---")
    raw_data = "Alice 13800138000 buy iPhone $999\nBob 13900139000 buy iPad $599"
    question = "总销售额是多少?"
    print(f"原始数据: {raw_data}\n")
    result = da_chain(raw_data, question)

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 步骤可校验: gate 在中间拦截 P0 工单 / 敏感词 / PII 残留")
    print("  - 失败可重试: gate 失败时把错误塞回 LLM 让它改")
    print("  - 对照通用性: 同一 chain 思维跨客服/数分两业务都好使")
    print("=" * 70)


if __name__ == "__main__":
    main()

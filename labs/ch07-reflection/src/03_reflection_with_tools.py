"""03 · Tool-Grounded Reflection — 工具锚定反思 (最强模式).

Andrew Ng Reflection Pattern (Variant 3 — most powerful):
    Reflection 不靠 LLM 自评, 而是**用真实工具的结果**作为反思依据.

例 (Example):
    LLM 写 Python 代码 → 真跑 → 看 traceback → 反思 → 改 → 再跑 → 通过

为什么"工具锚定"是最强模式 (Why most powerful):
    LLM 自己评自己有偏见 (model hallucinates 'looks good').
    工具 (compiler/database/test runner) 给的反馈是 ground truth (真实地基).

vs Ch6/03 SQL nuance:
    Ch6/03 是 generator + executor 角色分离 (workflow chain)
    本章是 *agent 自己反思 traceback 改代码* — 是 cognitive 行为

双业务:
    主 数分: LLM 写 pandas 代码 → 跑 → 报错 → 反思 → 改
    对照 客服: LLM 写客服回复 + 调 PII 检测工具 → 看哪里有 PII → 改

Run:
    python 03_reflection_with_tools.py
"""

from __future__ import annotations

import io
import re
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_llm  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402


# ============================================================
# 主业务: LLM 写 pandas 代码 → 真跑 → 看错改
# ============================================================


def safe_run_python(code: str, context_globals: dict | None = None) -> dict:
    """安全跑 Python 代码 (受限沙箱), 返回 stdout/stderr/exception."""
    g = {"__builtins__": __builtins__}  # 给个最小环境
    if context_globals:
        g.update(context_globals)

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code, g)  # noqa: S102 (教学场景)
        return {
            "ok": True,
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
        }
    except Exception as e:
        return {
            "ok": False,
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "exception": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-500:],
        }


def extract_code(text: str) -> str:
    """从 LLM 输出抽 ```python ...``` 代码块."""
    m = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def da_tool_grounded_reflection(task: str, max_rounds: int = 4) -> dict:
    """数据分析师用 pandas 算东西, 错了就反思改."""
    llm = get_llm(temperature=0.0)

    gen_prompt = ChatPromptTemplate.from_template(
        "You are a data analyst. Write Python code (using only standard library, "
        "NO external imports like pandas/numpy). Wrap code in ```python``` block.\n\n"
        "Task: {task}\n\n"
        "Previous error (if any):\n{prev_err}"
    )

    prev_err = "(no errors yet)"
    history = []

    for r in range(1, max_rounds + 1):
        print(f"\n  [Round {r}]")

        # 1. Generate code
        raw = (gen_prompt | llm | StrOutputParser()).invoke(
            {"task": task, "prev_err": prev_err}
        )
        code = extract_code(raw)
        print(f"  [Gen Code] {code[:100]}...")

        # 2. Execute (this IS the evaluator)
        result = safe_run_python(code)
        history.append({"round": r, "code": code, "result": result})

        if result["ok"]:
            print(f"  [Exec OK] stdout: {result['stdout'][:150]}")
            return {
                "final_code": code,
                "stdout": result["stdout"],
                "rounds": r,
                "history": history,
            }

        # 3. Reflect on traceback
        err_msg = result.get("exception", "") + "\n" + result.get("traceback", "")
        print(f"  [Exec FAIL] {result.get('exception', 'unknown')[:120]}")
        prev_err = err_msg[-400:]

    return {
        "rounds": max_rounds,
        "history": history,
        "max_rounds_hit": True,
        "last_err": prev_err,
    }


# ============================================================
# 对照业务: 客服回复 + PII 检测工具锚定
# ============================================================


def detect_pii(text: str) -> list[str]:
    """简单 PII 检测工具 — 找手机号/邮箱/身份证."""
    found = []
    if re.search(r"\b1\d{10}\b", text):
        found.append("phone_11_digits")
    if re.search(r"\b\d{17}[0-9X]\b", text):
        found.append("id_card_18")
    if re.search(r"[\w._%+-]+@[\w.-]+\.[A-Z]{2,}", text, re.IGNORECASE):
        found.append("email")
    return found


def cs_tool_grounded_reflection(message: str, max_rounds: int = 3) -> dict:
    """客服写回复 + PII 检测工具反思 (回复里不能含原始 PII)."""
    llm = get_llm()

    gen_prompt = ChatPromptTemplate.from_template(
        "You are a customer service rep. Reply to this message in 80 字以内 中文.\n"
        "IMPORTANT: Do NOT include any phone numbers, emails, or ID numbers in your reply.\n\n"
        "Message: {msg}\n\n"
        "Previous tool feedback (if any): {prev}"
    )

    prev_feedback = "(none)"
    history = []

    for r in range(1, max_rounds + 1):
        print(f"\n  [Round {r}]")
        reply = (gen_prompt | llm | StrOutputParser()).invoke(
            {"msg": message, "prev": prev_feedback}
        )
        print(f"  [Gen]    {reply[:100]}")

        # Tool: PII 检测 (这是 ground truth)
        pii = detect_pii(reply)
        print(f"  [Tool PII] found={pii}")

        history.append({"round": r, "reply": reply, "pii": pii})

        if not pii:
            print(f"  ✅ Round {r} 无 PII 残留, 通过")
            return {"final_reply": reply, "rounds": r, "history": history}

        # 反馈塞回 generator
        prev_feedback = (
            f"Your previous reply contained PII: {pii}. "
            f"Please rewrite without including any of these patterns."
        )

    return {
        "rounds": max_rounds,
        "history": history,
        "max_rounds_hit": True,
        "last_pii": history[-1]["pii"],
    }


def main() -> None:
    print("=" * 70)
    print("Ch7 · 03 Tool-Grounded Reflection (工具锚定反思) — 最强模式")
    print("=" * 70)

    # ===== 主业务: 数分 (LLM 写代码 + 跑) =====
    print("\n--- [主业务] 数据分析: LLM 写 Python → 跑 → 反思 traceback → 改 ---")
    task = (
        "Given a list of sales numbers [1500, 2300, 1800, 3200, 2700], "
        "compute the median (中位数), the standard deviation (用 statistics module). "
        "Print both clearly."
    )
    print(f"任务: {task[:100]}...")
    result = da_tool_grounded_reflection(task, max_rounds=4)
    if "stdout" in result:
        print(f"\n  最终代码 (前 200 字):")
        print(f"    {result['final_code'][:200]}")
        print(f"  跑出: {result['stdout']}")
        print(f"  迭代轮数: {result['rounds']}")

    # ===== 对照业务: 客服 PII 锚定 =====
    print("\n\n--- [对照业务] 客服回复 + PII 检测工具锚定 ---")
    msg = "请帮我联系客户 13800138000 (李四), 邮箱 lisi@example.com, 通知他订单异常."
    print(f"客户消息: {msg}")
    result = cs_tool_grounded_reflection(msg, max_rounds=3)
    if "final_reply" in result:
        print(f"\n  最终回复 (无 PII): {result['final_reply']}")
        print(f"  迭代轮数: {result['rounds']}")
    else:
        print(f"\n  3 轮后仍有 PII: {result['last_pii']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - 工具结果 = ground truth (无幻觉, 比 LLM 自评强)")
    print("  - traceback 是最好的反思依据: '哪行错+什么类型错' → LLM 知道改哪")
    print("  - 这就是 Cursor / Claude Code / Aider 等编码 Agent 的核心机制")
    print("=" * 70)


if __name__ == "__main__":
    main()

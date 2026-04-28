"""06 · Evolution Compare — 同 query 跑 L1-L5 对比.

This is the "money shot" 演化总览 — 学员一眼看清:
  - 简单 query: L1 性价比之王
  - 中等 query: L3-L4 平衡
  - 复杂 query: L5 不可替代

Chase 论点的实证: 不要"all-Agent", 而是按 query 复杂度选级.

Run:
    python 06_evolution_compare.py
"""

from __future__ import annotations

import importlib.util as _il
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None


# 动态加载各级 handler
def load(file_name: str):
    spec = _il.spec_from_file_location(
        file_name.replace(".py", ""), Path(__file__).parent / file_name
    )
    mod = _il.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


print("Loading L1-L5 handlers...")
l1 = load("01_l1_hardcoded.py")
l2 = load("02_l2_single_call.py")
l3 = load("03_l3_chain_workflow.py")
l4 = load("04_l4_router.py")
l5 = load("05_l5_autonomous_agent.py")


def compare(query: str, levels: list[str]) -> None:
    print(f"\n{'='*80}")
    print(f"Q: {query}")
    print("=" * 80)

    handlers = {
        "L1": l1.l1_handle,
        "L2": l2.l2_handle,
        "L3": l3.l3_handle,
        "L4": l4.l4_handle,
        "L5": l5.l5_handle,
    }

    print(f"{'Level':<6} {'耗时':<10} {'成本':<10} {'答复 (前 80 字)'}")
    print("-" * 100)

    for lv in levels:
        try:
            result = handlers[lv](query)
            ans = result.get("answer", "")[:80]
            ms = result.get("ms", 0)
            cost = result.get("cost", 0)
            print(f"{lv:<6} {ms:>6.0f}ms   ¥{cost:.4f}   {ans}")
        except Exception as e:
            print(f"{lv:<6} ERROR: {type(e).__name__}: {str(e)[:60]}")


def main() -> None:
    print("=" * 80)
    print("Ch9 · 06 Evolution Compare — 同 query 在 L1-L5 上跑")
    print("=" * 80)

    # 简单 query: L1 应足够
    compare("退货政策什么样?", ["L1", "L2", "L3", "L4"])

    # 中等 query: L1 处理不了, L3+ 合适
    compare("我那双鞋开胶了急用!", ["L1", "L2", "L3", "L4"])

    # 多步复杂 query: 只有 L5 能完整解决
    compare(
        "我订单 O20260427 鞋子开胶, 退款 ¥599, 给我发 50 元券补偿",
        ["L4", "L5"],
    )

    print("\n" + "=" * 80)
    print("📊 演化总结 (Evolution Summary)")
    print("=" * 80)
    print(
        """
    【简单 FAQ】   "退货政策"        → L1 0ms 0¥ 完美 (L5 浪费)
    【口语化】     "鞋子开胶急用"    → L3 ~3s 性价比高 (L1 命中不了)
    【多步任务】   "查单+退款+发券"  → L5 ~8s 不可替代 (L4 单意图搞不了)

    Chase 论点 (Chase's Argument):
      Cognitive architecture = your routing decision tree
      = "哪些 query 走哪级" — 这是你的护城河, 不外包.

      Agent infrastructure = LangGraph / DeepAgents
      = LLM 调用 / 状态机 / 持久化 — 这些外包给框架, 别自己造轮子.

    实战策略 (Production Strategy):
      Layer 0 - Cache       (语义缓存命中)
      Layer 1 - L1          (硬编码 FAQ, 70% 流量)
      Layer 2 - L3          (RAG chain, 20% 流量)
      Layer 3 - L5          (复杂 Agent, 10% 流量)
      → 综合 cost 比 all-L5 便宜 5-10x, 综合 quality 高 (该用大炮的地方用大炮)
    """
    )


if __name__ == "__main__":
    main()

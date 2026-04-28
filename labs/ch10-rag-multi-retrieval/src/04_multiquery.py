"""04 · MultiQuery — LLM 把 query 改写成多个变体.

核心: 用户的 query 可能只是问题的一个角度, LLM 改写出 N 个等价/相关 query,
分别检索后合并去重 → 召回更全面.

举例: 用户问 "退货政策" → LLM 改写:
    1. 商品退回流程是怎样的?
    2. 哪些情况支持无理由退货?
    3. 退货后多久能收到退款?

Run:
    python src/04_multiquery.py

教学要点:
    - LangChain MultiQueryRetriever.from_llm 内置 prompt + 解析
    - 默认生成 3 个变体 (可调 parser)
    - 适合: 用户问题模糊 / 多角度的场景
    - 不适合: 关键词类 / 一字千金的精准查询
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, build_vector_store, load_chunks  # noqa: E402
from common.llm import get_llm  # noqa: E402
from langchain_classic.retrievers.multi_query import MultiQueryRetriever  # noqa: E402

# 打开 INFO 日志, 看 LLM 改写后的变体 query
logging.basicConfig(level=logging.WARNING)
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)


def main() -> None:
    print("=" * 70)
    print("Ch10 · 04 · MultiQuery — LLM 改写 query 多角度召回")
    print("=" * 70)

    print("\n[Step 1] 加载 + 向量化")
    chunks = load_chunks()
    vs = build_vector_store(chunks)
    print(f"  {len(chunks)} chunks 入库")

    print("\n[Step 2] 构建 MultiQueryRetriever")
    base = vs.as_retriever(search_kwargs={"k": 5})
    mq = MultiQueryRetriever.from_llm(retriever=base, llm=get_llm())

    print("\n[Step 3] 跑 EVAL_QUERIES (每个 query LLM 改写成 3 个变体)")
    print("-" * 70)
    print(f"{'Query':<32}{'Hit@5':<10}Top-1 source")
    print("-" * 70)

    hit_count = 0
    top1_hit = 0
    total_lat_ms = 0.0
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        results = mq.invoke(query)
        total_lat_ms += (time.time() - t0) * 1000

        # MultiQuery 合并去重后可能多于 5, 截 top-5
        results = results[:5]
        sources = [r.metadata.get("source", "?") for r in results]
        hit = expected in sources
        if hit:
            hit_count += 1
        if sources and sources[0] == expected:
            top1_hit += 1

        mark = "✅" if hit else "❌"
        print(f"{query[:30]:<32}{mark:<10}{sources[0] if sources else 'N/A'}")

    print("-" * 70)
    print(f"\nHit@5: {hit_count}/{len(EVAL_QUERIES)} = {hit_count/len(EVAL_QUERIES)*100:.0f}%")
    print(f"Top-1 命中: {top1_hit}/{len(EVAL_QUERIES)}")
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.0f}ms / query  (1 LLM call + N embedding)")
    print("\n💡 召回更全面但贵了一次 LLM 调用 — 适合需要高 Recall 的场景.")


if __name__ == "__main__":
    main()

"""03 · Hybrid Search — BM25 + Dense + RRF 融合.

核心: BM25 召回关键词类, Dense 召回同义词类, RRF (Reciprocal Rank Fusion)
按排名融合 — 不依赖各自分数尺度 (BM25 0-30 vs cosine 0-1, 硬合无意义).

RRF 公式:
    RRF_score(d) = sum_over_retrievers( 1 / (k + rank_i(d)) )
    通常 k=60. 排名越靠前贡献越大, 跨 retriever 加和.

Run:
    python src/03_hybrid_rrf.py

教学要点:
    - LangChain EnsembleRetriever 内置 RRF (langchain_classic.retrievers)
    - weights=[0.5, 0.5] 控制相对权重 (调试用)
    - 业界数据: 加 BM25 让 Recall@10 从 65% → 91% (Supermemory benchmark)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, bm25_preprocess, build_vector_store, load_chunks  # noqa: E402
from langchain_classic.retrievers import EnsembleRetriever  # noqa: E402
from langchain_community.retrievers import BM25Retriever  # noqa: E402


def build_hybrid_retriever(chunks, k: int = 5):
    """BM25 + Dense + RRF 融合."""
    bm25 = BM25Retriever.from_documents(chunks, preprocess_func=bm25_preprocess, k=k)

    vs = build_vector_store(chunks)
    dense = vs.as_retriever(search_kwargs={"k": k})

    return EnsembleRetriever(retrievers=[bm25, dense], weights=[0.5, 0.5])


def main() -> None:
    print("=" * 70)
    print("Ch10 · 03 · Hybrid RRF — BM25 + Dense + Reciprocal Rank Fusion")
    print("=" * 70)

    print("\n[Step 1] 加载语料")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks")

    print("\n[Step 2] 构建 Hybrid Retriever (BM25 + Dense, RRF 融合)")
    t0 = time.time()
    hybrid = build_hybrid_retriever(chunks, k=5)
    print(f"  初始化耗时 {(time.time() - t0):.2f}s (含 embedding API)")

    print("\n[Step 3] 跑 EVAL_QUERIES top-5")
    print("-" * 70)
    print(f"{'Query':<32}{'Hit@5':<10}Top-1 source")
    print("-" * 70)

    hit_count = 0
    top1_hit = 0
    total_lat_ms = 0.0
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        results = hybrid.invoke(query)
        total_lat_ms += (time.time() - t0) * 1000

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
    print(f"Top-1 命中: {top1_hit}/{len(EVAL_QUERIES)}  (BM25 + Dense 互补)")
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.0f}ms / query")
    print("\n💡 RRF 不依赖分数尺度, 只看排名 — 这是它强于'加权求和'的根本原因.")


if __name__ == "__main__":
    main()

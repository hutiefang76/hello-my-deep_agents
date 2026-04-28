"""01 · Baseline — 纯 Dense 向量召回.

进化路径起点: InMemoryVectorStore + DashScope text-embedding-v3.
看每个 query top-5 的命中情况, 作为后续 6 个高级方案的对照基准.

Run:
    python src/01_baseline_dense.py

教学要点:
    - bi-encoder 相似度: query / doc 各自编码 → 余弦
    - 优势: 同义词召回 (退款 vs 退货)
    - 劣势: 关键词/型号易丢 (E1102 / qwen-plus)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, build_vector_store, load_chunks  # noqa: E402


def main() -> None:
    print("=" * 70)
    print("Ch10 · 01 · Baseline Dense — InMemoryVectorStore + DashScope v3")
    print("=" * 70)

    print("\n[Step 1] 加载 + 切分语料")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks 来自 {len({c.metadata['source'] for c in chunks})} 篇 doc")

    print("\n[Step 2] 向量化入库 (DashScope text-embedding-v3, 1024 维)")
    t0 = time.time()
    vs = build_vector_store(chunks)
    print(f"  入库耗时 {(time.time() - t0):.2f}s")

    print("\n[Step 3] 跑 EVAL_QUERIES top-5")
    print("-" * 70)
    print(f"{'Query':<32}{'Top-1 命中?':<14}Top-1 source")
    print("-" * 70)

    hit_count = 0
    total_lat_ms = 0.0
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        results = vs.similarity_search(query, k=5)
        total_lat_ms += (time.time() - t0) * 1000

        sources = [r.metadata.get("source", "?") for r in results]
        hit = expected in sources
        if hit:
            hit_count += 1
        mark = "✅" if results and results[0].metadata.get("source") == expected else "❌"
        print(f"{query[:30]:<32}{mark:<14}{sources[0] if sources else 'N/A'}")

    print("-" * 70)
    print(f"\nHit@5: {hit_count}/{len(EVAL_QUERIES)} = {hit_count/len(EVAL_QUERIES)*100:.0f}%")
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.0f}ms / query")
    print("\n💡 后续脚本会逐步引入 BM25 / Hybrid / MultiQuery / HyDE / Reranker.")


if __name__ == "__main__":
    main()

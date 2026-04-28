"""02 · 纯 BM25 — Lexical / 关键词召回.

经典 TF-IDF 改良版. 处理"专有名词/型号/错误码"比向量好得多 —
向量会"语义模糊化", 把 E1102 当成"某种数字代号"; BM25 是字符级精准匹配.

Run:
    python src/02_bm25_only.py

教学要点:
    - 中文 BM25 必须配合 jieba 分词 (默认按字符切召回会很差)
    - LangChain BM25Retriever.from_documents(preprocess_func=...) 接入分词器
    - 不需要 embedding API, 速度极快 (毫秒级)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, bm25_preprocess, load_chunks  # noqa: E402
from langchain_community.retrievers import BM25Retriever  # noqa: E402


def main() -> None:
    print("=" * 70)
    print("Ch10 · 02 · BM25 Only — Lexical 关键词召回")
    print("=" * 70)

    print("\n[Step 1] 加载语料")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks")

    print("\n[Step 2] 构建 BM25 索引 (jieba 中文分词)")
    t0 = time.time()
    bm25 = BM25Retriever.from_documents(
        chunks, preprocess_func=bm25_preprocess, k=5
    )
    print(f"  索引构建 {(time.time() - t0)*1000:.1f}ms (无需 API 调用!)")

    print("\n[Step 3] 跑 EVAL_QUERIES top-5")
    print("-" * 70)
    print(f"{'Query':<32}{'Hit@5':<10}Top-1 source")
    print("-" * 70)

    hit_count = 0
    top1_hit = 0
    total_lat_ms = 0.0
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        results = bm25.invoke(query)
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
    print(f"Top-1 命中: {top1_hit}/{len(EVAL_QUERIES)}")
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.1f}ms / query  (vs Dense ~50-200ms)")
    print("\n💡 BM25 在'退款 vs 退货'类同义词上会差; 但 'E1102' / 'qwen-plus' 这种关键词比 Dense 好.")


if __name__ == "__main__":
    main()

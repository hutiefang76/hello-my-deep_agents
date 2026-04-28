"""07 · Recall Compare — 6 个配置在同一 Q-set 上对比 Hit@5 / Top-1 / MRR / 延迟.

把 01-06 的 6 个方案放到同一组 EVAL_QUERIES 上跑, 输出对比表 —
让学员一眼看清"baseline → reranker"完整进化的收益.

指标:
    Hit@5  : top-5 中是否含 expected source 的任一 chunk
    Top-1  : top-1 是否就是 expected source (即 MRR=1 时的子条件)
    MRR    : Mean Reciprocal Rank, 1/rank (rank 是首个正确 chunk 的位置)
    延迟    : 单 query 召回耗时 (ms), 含 LLM/embedding 调用

Run:
    python src/07_recall_compare.py
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, bm25_preprocess, build_vector_store, load_chunks  # noqa: E402
from common.llm import get_llm  # noqa: E402
from langchain_classic.retrievers import EnsembleRetriever  # noqa: E402
from langchain_classic.retrievers.multi_query import MultiQueryRetriever  # noqa: E402
from langchain_community.retrievers import BM25Retriever  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

# 静默 MultiQuery 的 INFO 日志, 不影响主表
logging.basicConfig(level=logging.WARNING)


# ---------- 复用 06 的 LLM rerank ----------

import re

LLM_RERANK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是相关性评判员. 给定查询和 N 个候选片段, "
            "为每个片段输出 0-10 分相关性. 严格按格式 'index=分数', 共 {n} 行, 不解释.",
        ),
        ("human", "查询: {query}\n\n候选片段:\n{candidates}\n\n请输出 {n} 行评分."),
    ]
)


def llm_rerank(query: str, docs: list[Document], llm, top_k: int = 5) -> list[Document]:
    if not docs:
        return []
    candidates_text = "\n".join(f"[{i}] {d.page_content[:300]}" for i, d in enumerate(docs))
    resp = (LLM_RERANK_PROMPT | llm).invoke(
        {"query": query, "candidates": candidates_text, "n": len(docs)}
    )
    text = resp.content if hasattr(resp, "content") else str(resp)
    scores: dict[int, float] = {}
    for line in text.splitlines():
        m = re.search(r"(\d+)\s*[=:\s]\s*(-?\d+(?:\.\d+)?)", line)
        if m and 0 <= int(m.group(1)) < len(docs):
            scores[int(m.group(1))] = float(m.group(2))
    ranked = sorted(range(len(docs)), key=lambda i: scores.get(i, 0.0), reverse=True)
    return [docs[i] for i in ranked[:top_k]]


# ---------- HyDE ----------

HYDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是知识库写手. 给定问题, 写一段 100-150 字假设答案 (陈述句, 不需准确). 直接输出."),
        ("human", "{question}"),
    ]
)


def hyde_search(question: str, vs, llm, k: int = 5) -> list[Document]:
    hypo = (HYDE_PROMPT | llm).invoke({"question": question})
    hypo_text = hypo.content if hasattr(hypo, "content") else str(hypo)
    return vs.similarity_search(hypo_text, k=k)


# ---------- 评估 ----------

def evaluate(name: str, retrieve_fn) -> dict:
    """对一种 retrieve_fn 跑全部 EVAL_QUERIES, 返回指标 dict."""
    hit5 = 0
    top1 = 0
    rr_sum = 0.0
    latencies: list[float] = []

    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        try:
            results = retrieve_fn(query)[:5]
        except Exception as e:
            print(f"    ⚠️  {name} on '{query}' 出错: {type(e).__name__}: {e}")
            results = []
        latencies.append((time.time() - t0) * 1000)

        sources = [r.metadata.get("source", "?") for r in results]
        if expected in sources:
            hit5 += 1
        if sources and sources[0] == expected:
            top1 += 1
        # MRR: 找到 expected 在第几位
        rr = 0.0
        for i, s in enumerate(sources, 1):
            if s == expected:
                rr = 1.0 / i
                break
        rr_sum += rr

    n = len(EVAL_QUERIES)
    return {
        "name": name,
        "hit5": f"{hit5}/{n} ({hit5/n*100:.0f}%)",
        "top1": f"{top1}/{n} ({top1/n*100:.0f}%)",
        "mrr": f"{rr_sum/n:.3f}",
        "lat_ms": f"{sum(latencies)/n:.0f}",
    }


def main() -> None:
    print("=" * 78)
    print("Ch10 · 07 · Recall Compare — 6 配置 × 10 queries 全量对比")
    print("=" * 78)

    print("\n[Setup] 加载语料 + 向量化 (一次, 6 个配置共享)")
    chunks = load_chunks()
    vs = build_vector_store(chunks)
    llm = get_llm()
    bm25 = BM25Retriever.from_documents(chunks, preprocess_func=bm25_preprocess, k=5)
    bm25_top20 = BM25Retriever.from_documents(chunks, preprocess_func=bm25_preprocess, k=20)
    dense = vs.as_retriever(search_kwargs={"k": 5})
    dense_top20 = vs.as_retriever(search_kwargs={"k": 20})
    hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.5, 0.5])
    hybrid_top20 = EnsembleRetriever(
        retrievers=[bm25_top20, dense_top20], weights=[0.5, 0.5]
    )
    print(f"  {len(chunks)} chunks 共享给 6 个配置")

    print("\n[Run] 跑 6 个配置 × {} queries (含 LLM 调用, 估计 1-3 分钟)".format(len(EVAL_QUERIES)))
    print("-" * 78)

    results: list[dict] = []

    print("  → 01 baseline_dense ...")
    results.append(evaluate("01_baseline_dense", lambda q: vs.similarity_search(q, k=5)))

    print("  → 02 bm25_only ...")
    results.append(evaluate("02_bm25_only", lambda q: bm25.invoke(q)))

    print("  → 03 hybrid_rrf ...")
    results.append(evaluate("03_hybrid_rrf", lambda q: hybrid.invoke(q)))

    print("  → 04 multiquery (LLM 改写, 慢) ...")
    mq = MultiQueryRetriever.from_llm(retriever=dense, llm=llm)
    results.append(evaluate("04_multiquery", lambda q: mq.invoke(q)))

    print("  → 05 hyde (LLM 生假设, 慢) ...")
    results.append(evaluate("05_hyde", lambda q: hyde_search(q, vs, llm, k=5)))

    print("  → 06 reranker (hybrid top-20 → LLM rerank top-5, 最慢) ...")
    results.append(
        evaluate(
            "06_reranker",
            lambda q: llm_rerank(q, hybrid_top20.invoke(q), llm, top_k=5),
        )
    )

    print("-" * 78)
    print()

    # ---------- 输出表格 ----------
    print("=" * 78)
    print("📊 Recall Compare — RAG 多路召回 6 方案对比 (10 queries)")
    print("=" * 78)
    header = f"{'配置':<24}{'Hit@5':<14}{'Top-1':<14}{'MRR':<10}{'延迟(ms)':<12}"
    print(header)
    print("-" * 78)
    for r in results:
        row = f"{r['name']:<24}{r['hit5']:<14}{r['top1']:<14}{r['mrr']:<10}{r['lat_ms']:<12}"
        print(row)
    print("-" * 78)

    # ---------- markdown 版本 (易复制到 README) ----------
    print("\n--- 同上, markdown 版 (复制到 README) ---\n")
    print("| 配置 | Hit@5 | Top-1 | MRR | 延迟(ms) |")
    print("|---|---|---|---|---|")
    for r in results:
        print(f"| {r['name']} | {r['hit5']} | {r['top1']} | {r['mrr']} | {r['lat_ms']} |")

    print("\n💡 关键观察:")
    print("  • Hit@5 在小语料下容易饱和; Top-1 / MRR 才能区分召回质量")
    print("  • BM25 延迟最低 (无 API 调用), 但语义类 query 弱")
    print("  • Hybrid RRF 是免费午餐 — 无需新模型, 召回质量↑")
    print("  • MultiQuery / HyDE 都需要额外 LLM 调用, 适合复杂查询")
    print("  • Reranker 让 Top-1 显著提升, 这是生产 RAG 的标配优化")


if __name__ == "__main__":
    main()

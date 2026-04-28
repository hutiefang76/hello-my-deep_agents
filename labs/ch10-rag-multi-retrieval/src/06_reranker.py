"""06 · Reranker — 二次精排.

核心: 第一阶段召回 top-20 (高 Recall), 用更贵但更准的模型把 top-20 重新排序到
top-5 (高 Precision). 这是生产 RAG 的"标配优化".

为什么有效:
    召回 (bi-encoder)  : query, doc 各自编码 → 余弦. 单次推理快但精度低.
    精排 (cross-encoder): query+doc 拼起来过注意力. 精度高但每对都算一遍.
    所以只对 top-N 用精排, N 通常 10-100.

本脚本默认实现: LLM-based listwise rerank (零额外依赖, 真能跑).
可选实现     : BAAI/bge-reranker-base (HuggingFace cross-encoder, 装了 sentence-transformers + torch 才启用).

Run:
    python src/06_reranker.py

教学要点:
    - 召回 + 精排的两阶段范式
    - LLM rerank 无需额外模型, 但每次精排都消耗 tokens
    - BGE reranker 一次性下载, 推理便宜, 适合生产
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, bm25_preprocess, build_vector_store, load_chunks  # noqa: E402
from common.llm import get_llm  # noqa: E402
from langchain_classic.retrievers import EnsembleRetriever  # noqa: E402
from langchain_community.retrievers import BM25Retriever  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402


# ---------- LLM-based Reranker (主路, 零依赖) ----------

LLM_RERANK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是相关性评判员. 给定一个查询和 N 个候选片段, "
            "为每个片段输出一个 0-10 的相关性分数 (10=完美匹配, 0=完全无关). "
            "严格按格式输出: 每行 'index=分数', 不解释. 共 {n} 行.",
        ),
        (
            "human",
            "查询: {query}\n\n候选片段:\n{candidates}\n\n请输出 {n} 行评分.",
        ),
    ]
)


def llm_rerank(query: str, docs: list[Document], llm, top_k: int = 5) -> list[Document]:
    """用 LLM 给候选文档打分, 取 top_k.

    输入: docs 是召回的 N 个候选 (通常 N=10-20)
    输出: 按分数降序的前 top_k
    """
    if not docs:
        return []
    candidates_text = "\n".join(
        f"[{i}] {d.page_content[:300]}" for i, d in enumerate(docs)
    )
    chain = LLM_RERANK_PROMPT | llm
    resp = chain.invoke({"query": query, "candidates": candidates_text, "n": len(docs)})
    text = resp.content if hasattr(resp, "content") else str(resp)

    # 解析 'index=分数' 格式 (容错: 兼容 '0=8' / '0: 8' / '0 8')
    scores: dict[int, float] = {}
    for line in text.splitlines():
        m = re.search(r"(\d+)\s*[=:\s]\s*(-?\d+(?:\.\d+)?)", line)
        if m:
            idx = int(m.group(1))
            score = float(m.group(2))
            if 0 <= idx < len(docs):
                scores[idx] = score

    # 没解析出来的给 0 (落到末尾)
    ranked_idx = sorted(
        range(len(docs)), key=lambda i: scores.get(i, 0.0), reverse=True
    )
    return [docs[i] for i in ranked_idx[:top_k]]


# ---------- BGE Reranker (备选, try-import 优雅降级) ----------

def try_bge_rerank(query: str, docs: list[Document], top_k: int = 5):
    """尝试 BGE Reranker. 若 sentence-transformers / torch 没装, 返回 None."""
    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except ImportError:
        return None
    try:
        ce = CrossEncoder("BAAI/bge-reranker-base", max_length=512)
        pairs = [[query, d.page_content[:512]] for d in docs]
        scores = ce.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [d for d, _ in ranked[:top_k]]
    except Exception as e:
        print(f"  ⚠️  BGE reranker 加载失败 ({type(e).__name__}), fallback to LLM rerank")
        return None


def main() -> None:
    print("=" * 70)
    print("Ch10 · 06 · Reranker — 召回 top-20 → 精排 top-5")
    print("=" * 70)

    print("\n[Step 1] 加载 + 构建 hybrid 召回 (top-20)")
    chunks = load_chunks()
    vs = build_vector_store(chunks)
    bm25 = BM25Retriever.from_documents(chunks, preprocess_func=bm25_preprocess, k=20)
    dense = vs.as_retriever(search_kwargs={"k": 20})
    hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.5, 0.5])
    print(f"  {len(chunks)} chunks 入库, 召回阶段 top-20")

    print("\n[Step 2] 选择 reranker 实现")
    use_bge_test = try_bge_rerank("test", chunks[:1], top_k=1)
    if use_bge_test is not None:
        rerank_mode = "BGE (BAAI/bge-reranker-base, cross-encoder)"
        print(f"  ✅ {rerank_mode}")
    else:
        rerank_mode = "LLM listwise (qwen-plus 打分)"
        print(f"  ✅ {rerank_mode}")
        print("  💡 装 sentence-transformers + torch 可启用 BGE reranker")

    llm = get_llm()

    print("\n[Step 3] 跑 EVAL_QUERIES — 召回 top-20 → 精排 top-5")
    print("-" * 70)
    print(f"{'Query':<32}{'Hit@5':<10}Top-1 source")
    print("-" * 70)

    hit_count = 0
    top1_hit = 0
    total_lat_ms = 0.0
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        candidates = hybrid.invoke(query)  # top-20
        # 试 BGE, 失败则 LLM rerank
        bge_result = try_bge_rerank(query, candidates, top_k=5)
        if bge_result is not None:
            results = bge_result
        else:
            results = llm_rerank(query, candidates, llm, top_k=5)
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
    print(f"Top-1 命中: {top1_hit}/{len(EVAL_QUERIES)}  (精排让 Top-1 显著上升)")
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.0f}ms / query")
    print(f"使用的 reranker: {rerank_mode}")
    print("\n💡 业界数据: hybrid + reranker 让 Recall@5 从 78% → 92% (Analytics Vidhya 2024-12).")


if __name__ == "__main__":
    main()

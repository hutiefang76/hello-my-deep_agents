"""05 · HyDE — Hypothetical Document Embeddings.

核心思想 (Gao et al., 2022, https://arxiv.org/abs/2212.10496):
    短 query 的 embedding 与长文档 embedding 的语义分布有差异.
    解法: 让 LLM 先"编"一个**假设答案**, 用假设答案的 embedding 检索 —
    这个假设答案虽然内容不一定准, 但风格/长度/分布更接近真实文档.

流程:
    Query  ──LLM──►  Hypothetical Doc  ──embedding──►  vector store
                          (~150 字)                           ↓
                                                       top-K real docs

Run:
    python src/05_hyde.py

教学要点:
    - 不用 LangChain 内置 (它 prompt 较僵), 自己写 30 行更清楚
    - 适合: 事实型 / 知识问答 (假设答案能"猜"得相对靠谱)
    - 不适合: 主观型 / 创作型 query
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _corpus import EVAL_QUERIES, build_vector_store, load_chunks  # noqa: E402
from common.llm import get_llm  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

HYDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是知识库写手. 给定用户问题, 写一段 100-150 字的'假设答案' — "
            "假装你已经知道答案, 用陈述句 (不是问句) 给出可能的回答. "
            "不需要事实正确, 只要语言风格像内部文档. 直接输出答案, 不加任何前缀.",
        ),
        ("human", "问题: {question}"),
    ]
)


def hyde_retrieve(question: str, vs, llm, k: int = 5):
    """1) LLM 写假设文档 → 2) 用假设文档 embedding 检索."""
    chain = HYDE_PROMPT | llm
    hypo = chain.invoke({"question": question})
    hypo_text = hypo.content if hasattr(hypo, "content") else str(hypo)
    # 注意: 这里用 hypo_text 检索, 不是用 question
    return hypo_text, vs.similarity_search(hypo_text, k=k)


def main() -> None:
    print("=" * 70)
    print("Ch10 · 05 · HyDE — Hypothetical Document Embeddings")
    print("=" * 70)

    print("\n[Step 1] 加载 + 向量化")
    chunks = load_chunks()
    vs = build_vector_store(chunks)
    llm = get_llm()
    print(f"  {len(chunks)} chunks 入库")

    print("\n[Step 2] 跑 EVAL_QUERIES (每个 query 先生成假设文档再检索)")
    print("-" * 70)
    print(f"{'Query':<32}{'Hit@5':<10}Top-1 source")
    print("-" * 70)

    hit_count = 0
    top1_hit = 0
    total_lat_ms = 0.0
    sample_hypo = None
    sample_q = None
    for query, expected in EVAL_QUERIES:
        t0 = time.time()
        hypo, results = hyde_retrieve(query, vs, llm, k=5)
        total_lat_ms += (time.time() - t0) * 1000
        if sample_hypo is None:
            sample_hypo = hypo
            sample_q = query

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
    print(f"平均延迟: {total_lat_ms/len(EVAL_QUERIES):.0f}ms / query  (LLM 生假设 + embedding)")

    if sample_hypo:
        print(f"\n💡 假设文档样例:")
        print(f"  原 query: {sample_q}")
        print(f"  hypo doc (前 200 字): {sample_hypo[:200]}...")


if __name__ == "__main__":
    main()

# RAG 多路召回 · Multi-Retrieval Hybrid Search · Reranker

> 用户原始目标 #3 明确点名"RAG 多路召回"——这是当前教程**最大缺口**(0 实现)。本文档汇总业界主流方案与原文出处。

---

## 1. 主流多路召回架构 (2025-2026)

```
                          ┌──────────────────┐
   User Query  ───────►  │  Query Rewrite   │ (MultiQuery / HyDE)
                          └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
       │  BM25       │     │  Dense      │     │  Sparse      │
       │  (lexical)  │     │  (vector)   │     │  (SPLADE)    │
       └──────┬──────┘     └──────┬──────┘     └──────┬───────┘
              │                   │                   │
              └───────────┬───────┴───────────────────┘
                          ▼
                  ┌──────────────────┐
                  │  RRF Fusion      │ (Reciprocal Rank Fusion)
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Reranker        │ (BGE Reranker / Cohere / ColBERT)
                  └────────┬─────────┘
                           │
                           ▼
                       Top-K 给 LLM
```

---

## 2. 各组件详解

### 2.1 BM25 (Lexical / Sparse)

**原理**: 经典 TF-IDF 进化版，关键词命中越精准越好。
**优势**: 处理专有名词/型号/代码片段比向量好(向量会"语义模糊化")。
**劣势**: 无法处理同义词。

**LangChain 实现**:
```python
from langchain_community.retrievers import BM25Retriever
bm25 = BM25Retriever.from_documents(docs)
```

### 2.2 Dense (Vector / Semantic)

**原理**: Embedding 后算余弦相似度。
**优势**: 处理同义词/释义。
**劣势**: 专有名词/数字/型号容易丢。

### 2.3 RRF (Reciprocal Rank Fusion)

**公式**: `RRF_score(d) = sum_over_retrievers( 1 / (k + rank_i(d)) )` , 通常 k=60。

**为什么用 RRF 不用加权求和**:
- 各 retriever 的分数不同尺度(BM25 是 0-30, 向量是 0-1)，硬合无意义
- RRF 只看排名，scale-invariant

**LangChain 实现**:
```python
from langchain.retrievers import EnsembleRetriever
ensemble = EnsembleRetriever(retrievers=[bm25, vector_retriever], weights=[0.5, 0.5])
```

### 2.4 MultiQuery Retriever

**原理**: 用 LLM 把原 query 改写成多个变体，每个分别检索后合并。
**论文**: "Multi-query retrieval: synthesize the user's original query into multiple perspectives."

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
mq = MultiQueryRetriever.from_llm(retriever=base, llm=llm)
# 自动生成 3 个变体 query, 各自检索, 合并去重
```

### 2.5 HyDE (Hypothetical Document Embeddings)

**原理**: 让 LLM **先编一个假设答案**，用这个假设答案的 embedding 去检索——比直接用 query embedding 更接近真实文档分布。
**论文**: Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels", 2022

**典型流程**:
1. Query: "退货政策怎么定的?"
2. LLM 生成假设答案: "退货政策一般规定 7 天无理由退货，需保持商品..."
3. 用假设答案的 embedding 检索真实文档

### 2.6 Reranker (二次精排)

**原理**: 第一阶段召回 top-50/100 后，用更贵但更准的 cross-encoder 模型精排到 top-5。
**主流模型**:
- BGE Reranker (BAAI, 中英双语)
- Cohere Rerank (商业 API)
- ColBERT (token-level late interaction)

**为什么有效**: 召回模型(bi-encoder)是把 query 和 doc 各自编码后算相似度——慢但单次推理快。Reranker(cross-encoder)是把 query+doc 拼起来做注意力——精度高但每对都要算一遍，所以只对 top-N 用。

---

## 3. 业界数据 (Recall@10 提升)

| 配置 | Recall@10 | 来源 |
|---|---|---|
| 纯 Dense (baseline) | 65-78% | Supermemory benchmark 2026-04 |
| BM25 + Dense + RRF | 91% | 同上 |
| 加 Reranker (BGE) | 95%+ | Analytics Vidhya 2024-12 |

**结论**: 多路召回不是花哨——是**生产级 RAG 的必需**。

---

## 4. 应落到本教程哪一章

**新增 Ch10 · RAG 多路召回**:

```
labs/ch10-rag-multi-retrieval/
├── README.md
├── docs/                       # 测试语料(沿用 ch04-2-3 的 product_faq/tech_stack/troubleshooting)
├── src/
│   ├── 01_baseline_dense.py        纯向量 baseline (Recall@10)
│   ├── 02_bm25_only.py             纯关键词 baseline
│   ├── 03_hybrid_rrf.py            BM25 + Dense + RRF (LangChain EnsembleRetriever)
│   ├── 04_multiquery.py            MultiQueryRetriever LLM 改写
│   ├── 05_hyde.py                  HyDE 假设文档 embedding
│   ├── 06_reranker.py              加 BGE Reranker / Cohere
│   └── 07_recall_compare.py        7 配置在同一组 Q 上对比 Hit Rate / MRR / 延迟
└── verify.sh
```

**评估指标**:
- Hit Rate @ K=5, 10
- MRR (Mean Reciprocal Rank)
- 延迟 (ms/query)
- 成本 (token + reranker call)

---

## 5. Sources (全部真实可点击)

### 学术与官方文档
- [Anthropic — Contextual Retrieval (2024-09)](https://www.anthropic.com/news/contextual-retrieval) — Anthropic 提出的 Contextual Embeddings + Hybrid Search
- [LangChain — EnsembleRetriever 官方文档](https://python.langchain.com/docs/how_to/ensemble_retriever/)
- [LangChain — MultiQueryRetriever](https://python.langchain.com/docs/how_to/MultiQueryRetriever/)
- [LangChain — HyDE Cookbook](https://python.langchain.com/docs/templates/hyde)
- [LlamaIndex — QueryFusionRetriever](https://docs.llamaindex.ai/en/stable/examples/retrievers/reciprocal_rerank_fusion/)

### 业界博客 (2024-2026)
- [Analytics Vidhya — Contextual RAG with Hybrid + Reranking (2024-12)](https://www.analyticsvidhya.com/blog/2024/12/contextual-rag-systems-with-hybrid-search-and-reranking/)
- [Prem Blog — Hybrid Search BM25+SPLADE+Vector (2026-03)](https://blog.premai.io/hybrid-search-for-rag-bm25-splade-and-vector-search-combined/)
- [Supermemory — Hybrid Search Guide (2026-04)](https://blog.supermemory.ai/hybrid-search-guide/)
- [Superlinked — Optimizing RAG with Hybrid Search & Reranking](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)
- [Meilisearch — Understanding Hybrid Search RAG](https://www.meilisearch.com/blog/hybrid-search-rag)
- [DEV — Advanced RAG: Naive→Hybrid→Reranking](https://dev.to/kuldeep_paul/advanced-rag-from-naive-retrieval-to-hybrid-search-and-re-ranking-4km3)
- [Medium — BM25 vs Sparse vs Hybrid](https://medium.com/@dewasheesh.rana/bm25-vs-sparse-vs-hybrid-search-in-rag-from-layman-to-pro-e34ff21c4ada)
- [ZeroEntropy — Choosing Best Reranking Model 2026](https://zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025/)

### Reference 实现
- [GitHub — Contextual RAG with Hybrid + Reranking](https://github.com/chatterjeesaurabh/Contextual-RAG-System-with-Hybrid-Search-and-Reranking)
- [BGE Reranker (HuggingFace)](https://huggingface.co/BAAI/bge-reranker-large)

### 论文
- [HyDE — Precise Zero-Shot Dense Retrieval (Gao et al., 2022)](https://arxiv.org/abs/2212.10496)
- [ColBERT — Efficient Passage Search (Khattab et al., 2020)](https://arxiv.org/abs/2004.12832)

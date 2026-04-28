# Ch 10 · RAG 多路召回 (Multi-Retrieval Hybrid Search)

> 用户原始目标 #3 明确点名 "**RAG 多路召回**" — 这是 Ch4.2.3 baseline RAG **没覆盖**的进阶必修.
> 本章一次看清 baseline → BM25 → Hybrid → MultiQuery → HyDE → Reranker 的完整进化路径, 每一步用同一组 query 实测对比.
>
> Ref: [docs/references/topics/rag-multi-retrieval.md](../../docs/references/topics/rag-multi-retrieval.md)

## 学完能力

- 看懂业界主流 7 种召回方案的**适用场景与代价**
- 用 LangChain 1.x (`langchain_classic`) 拼出 Hybrid + RRF 检索器
- 自己写 30 行实现 HyDE (假设文档 embedding) 和 LLM-based Reranker
- 用 Hit@5 / Top-1 / MRR / 延迟 四指标做严肃的检索系统评估

## 架构图

```
                        ┌──────────────────┐
        User Query ───► │  Query Rewrite   │  (04 MultiQuery / 05 HyDE)
                        └────────┬─────────┘
                                 │
            ┌────────────────────┼─────────────────────┐
            ▼                    ▼                     ▼
     ┌────────────┐       ┌────────────┐       ┌──────────────┐
     │  BM25      │       │  Dense     │       │  Sparse      │
     │ (lexical)  │       │ (vector)   │       │ (SPLADE,     │
     │ jieba 分词  │       │ DashScope  │       │  本章未做)    │
     │ 02         │       │ 01         │       │              │
     └─────┬──────┘       └─────┬──────┘       └──────────────┘
           │                    │
           └─────────┬──────────┘
                     ▼
            ┌────────────────────┐
            │  RRF Fusion        │  (03 Hybrid: EnsembleRetriever)
            └─────────┬──────────┘
                      │
                top-20 候选
                      ▼
            ┌────────────────────┐
            │  Reranker          │  (06: LLM-listwise / BGE)
            └─────────┬──────────┘
                      │
                  top-5 给 LLM
                      ▼
                  💬 Answer
```

## 7 脚本一览

| 脚本 | 一句话 | 跑法 |
|---|---|---|
| `01_baseline_dense.py` | 纯向量召回 baseline (DashScope text-embedding-v3) | `python src/01_baseline_dense.py` |
| `02_bm25_only.py` | 纯 BM25 + jieba 中文分词, 看关键词召回 | `python src/02_bm25_only.py` |
| `03_hybrid_rrf.py` | BM25 + Dense + RRF 融合 (EnsembleRetriever) | `python src/03_hybrid_rrf.py` |
| `04_multiquery.py` | LLM 改写 query 成 N 个变体, 各自召回合并 | `python src/04_multiquery.py` |
| `05_hyde.py` | LLM 先编假设答案, 用假设答案 embedding 检索 | `python src/05_hyde.py` |
| `06_reranker.py` | hybrid 召回 top-20 → reranker 精排 top-5 | `python src/06_reranker.py` |
| `07_recall_compare.py` | 6 配置 × 10 query 全量对比表 (集大成) | `python src/07_recall_compare.py` |

## 一键验证

```bash
bash verify.sh
```

依次会做: 环境检查 → 装增量依赖 (`rank_bm25` + `jieba`) → 跑 7 个脚本 → 输出对比表.

## 关键代码片段

### BM25 中文召回 (02)
```python
# 中文必须配 jieba 分词, 默认按字符切召回会很差
import jieba
from langchain_community.retrievers import BM25Retriever

bm25 = BM25Retriever.from_documents(
    chunks,
    preprocess_func=lambda t: [tok for tok in jieba.lcut(t) if tok.strip()],
    k=5,
)
results = bm25.invoke("E1102 错误码什么意思")
```

### Hybrid + RRF (03) — 业界主流
```python
from langchain_classic.retrievers import EnsembleRetriever  # ⚠️ langchain 1.x 路径

bm25_r = BM25Retriever.from_documents(chunks, preprocess_func=jieba_cut, k=5)
dense_r = vs.as_retriever(search_kwargs={"k": 5})
hybrid = EnsembleRetriever(retrievers=[bm25_r, dense_r], weights=[0.5, 0.5])
# weights 是 RRF 各 retriever 的相对权重, 内部 score = sum(w_i / (60 + rank_i))
```

### HyDE (05) — 30 行实现
```python
HYDE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是知识库写手. 写一段 100-150 字的假设答案, 陈述句, 不需要事实正确."),
    ("human", "{question}"),
])

def hyde_retrieve(question, vs, llm, k=5):
    hypo = (HYDE_PROMPT | llm).invoke({"question": question}).content
    return vs.similarity_search(hypo, k=k)  # 注意: 检索用 hypo 不用 question
```

### LLM-based Reranker (06) — 零额外依赖
```python
LLM_RERANK_PROMPT = "给查询和 N 个片段, 输出 N 行 'index=分数', 0-10 分."

def llm_rerank(query, docs, llm, top_k=5):
    cand = "\n".join(f"[{i}] {d.page_content[:300]}" for i, d in enumerate(docs))
    text = (LLM_RERANK_PROMPT | llm).invoke({...}).content
    scores = parse_scores(text)  # 正则抽 'index=分数'
    return [docs[i] for i in sorted(range(len(docs)), key=lambda i: -scores.get(i, 0))[:top_k]]
```

> 装了 `sentence-transformers + torch` 时 06 会自动启用真 BGE Reranker (`BAAI/bge-reranker-base`); 否则 fallback 到 LLM listwise rerank.

## 实测对比 (07 输出)

跑 `python src/07_recall_compare.py` 在 5 篇 markdown × 17 chunks × 10 queries 上得到:

| 配置 | Hit@5 | Top-1 | MRR | 延迟(ms) |
|---|---|---|---|---|
| 01_baseline_dense | 10/10 (100%) | 9/10 (90%) | 0.950 | 1644 |
| 02_bm25_only | 10/10 (100%) | 7/10 (70%) | 0.825 | **1** |
| 03_hybrid_rrf | 10/10 (100%) | 8/10 (80%) | 0.900 | 1690 |
| 04_multiquery | 10/10 (100%) | 8/10 (80%) | 0.900 | 8831 |
| 05_hyde | 10/10 (100%) | 9/10 (90%) | 0.950 | 7082 |
| 06_reranker | 10/10 (100%) | 9/10 (90%) | 0.933 | 5244 |

### 数据怎么读

1. **Hit@5 全 100% 不是方案厉害**, 是教学语料只有 5 篇 doc — top-5 自然能覆盖. 业界数据是百万级语料 + 千级 query 跑出来的.
2. **Top-1 / MRR 才是真区分** — Dense 0.950 vs BM25 0.825, 差 12 个百分点, 这是同义词召回的胜利 ("退款" → "退货").
3. **延迟梯度极陡**: BM25 = 1ms, Dense ~1.6s, Hybrid ~1.7s, MultiQuery ~9s, HyDE ~7s — 多一次 LLM 调用就是数千毫秒.
4. **教学 demo 下 Reranker 没明显胜出 (0.933)**, 因为候选本身只有 17 个 chunks. 业界数据 (Analytics Vidhya 2024-12) 在百万级语料 + top-100 召回场景: hybrid + reranker 让 Recall@5 从 78% → **92%**.
5. **业界数据 (Recall@10 提升, [Supermemory 2026-04](https://blog.supermemory.ai/hybrid-search-guide/))**:
   - 纯 Dense baseline: 65-78%
   - BM25 + Dense + RRF: **91%**
   - + BGE Reranker: **95%+**

## 何时该用 / 何时不该用 — 决策表

| 场景 | 推荐配置 | 不推荐配置 | 理由 |
|---|---|---|---|
| **MVP / 小语料 / 内部 wiki** | 01 baseline_dense | 06 reranker | 小语料下 Reranker 收益小, 不值得多 LLM 调用 |
| **关键词密集 / 错误码 / 型号** | 03 hybrid_rrf | 01 dense_only | BM25 是这类查询的"杀手锏" |
| **用户问题模糊 / 多角度** | 04 multiquery | 02 bm25_only | LLM 改写能补语义视角 |
| **事实型问答 / 知识库** | 05 hyde | 02 bm25_only | HyDE 假设文档 vs 短 query 嵌入分布更接近 |
| **生产 RAG / 高 SLA** | 03 + 06 (hybrid + reranker) | 任何单一方案 | 召回保 recall, 精排保 precision |
| **延迟敏感 / 实时** | 02 bm25_only or 03 hybrid | 04 / 05 / 06 (额外 LLM) | LLM rewrite 加几秒, 实时场景吃不消 |

## 常见坑 / 踩过的坑

- **`langchain.retrievers.X` ImportError**: langchain 1.x 已迁移到 `langchain_classic.retrievers`. 老代码搬到 1.x 必须改路径.
- **BM25 中文召回奇差**: 默认按空格切词, 中文需传 `preprocess_func=jieba.lcut`.
- **HyDE 用 hypo 检索, 不是 query**: 容易写错 — 别拿 `vs.similarity_search(question)` 当 HyDE.
- **MultiQuery 默认 verbose 日志**: 通过 `logging.getLogger("langchain.retrievers.multi_query").setLevel(WARNING)` 关掉.
- **Reranker LLM 输出解析容错**: LLM 不一定严格按 `index=分数` 输出, 用宽松正则 `(\d+)\s*[=:\s]\s*(-?\d+\.?\d*)`.

## 必读参考

- 设计依据: [docs/references/topics/rag-multi-retrieval.md](../../docs/references/topics/rag-multi-retrieval.md)
- 业界对标: [docs/references/benchmarks/mainstream-courses.md](../../docs/references/benchmarks/mainstream-courses.md)
- 上一节 baseline: [labs/ch04-2-3-tools-rag/README.md](../ch04-2-3-tools-rag/README.md)
- HyDE 原论文: [Gao et al., 2022](https://arxiv.org/abs/2212.10496)
- BGE Reranker: [BAAI/bge-reranker-base](https://huggingface.co/BAAI/bge-reranker-base)
- Anthropic Contextual Retrieval: <https://www.anthropic.com/news/contextual-retrieval>

## 下一步

学完多路召回 → 进 [Ch11 · Context Engineering](../ch11-context-engineering/) 系统化讲 LLM 注意力工程
(教程其他章节落地中).

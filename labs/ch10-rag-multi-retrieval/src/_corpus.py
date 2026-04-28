"""_corpus — Ch10 七脚本共享语料初始化.

避免重复 80 行 (load → split → embed) 代码.

主要导出:
    load_chunks()          -> list[Document]   按 markdown 标题切分
    build_vector_store()   -> InMemoryVectorStore
    bm25_preprocess(text)  -> list[str]        中文 jieba 分词 (BM25 必需)
    EVAL_QUERIES           -> list[(query, expected_source)]  ground truth
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))

from common.llm import get_embeddings  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402
from langchain_text_splitters import MarkdownTextSplitter  # noqa: E402


_DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def load_chunks(chunk_size: int = 500, overlap: int = 50) -> list[Document]:
    """加载 docs/*.md 并切分为 chunks."""
    docs: list[Document] = []
    for md_file in sorted(_DOCS_DIR.glob("*.md")):
        docs.append(
            Document(
                page_content=md_file.read_text(encoding="utf-8"),
                metadata={"source": md_file.name, "category": md_file.stem},
            )
        )
    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_documents(docs)


def build_vector_store(chunks: list[Document]) -> InMemoryVectorStore:
    """向量化入库 (DashScope text-embedding-v3)."""
    vs = InMemoryVectorStore(get_embeddings())
    vs.add_documents(chunks)
    return vs


def bm25_preprocess(text: str) -> list[str]:
    """中文 jieba 分词 — BM25 必需 (默认按字符切召回会很差).

    BM25Retriever 接受 preprocess_func, 我们传 jieba.lcut 即可.
    """
    import jieba  # 延迟导入, 不强制 dense 脚本装 jieba

    return [tok for tok in jieba.lcut(text) if tok.strip()]


# ---------- 评估集 (07_recall_compare.py 用) ----------
# 每条: (query, expected_source_basename)
# 标注覆盖 3 类难度: 语义类 / 关键词类 / 长尾类
EVAL_QUERIES: list[tuple[str, str]] = [
    # --- 语义类 (dense 强, BM25 不一定命中) ---
    ("退款会退到哪里去", "product_faq.md"),                    # query 用"退款", doc 写"退货退回"
    ("钻石会员有什么特权", "product_faq.md"),                   # 特权 vs 权益
    ("商品坏了怎么修", "product_faq.md"),                      # 修 vs 保修
    ("我们用的是什么数据库", "tech_stack.md"),                  # 数据库 vs PostgreSQL
    ("怎么观察 LLM 的调用链", "tech_stack.md"),                # 观察 vs 可观测性 trace
    # --- 关键词类 (BM25 强, 专有名词/型号/接口码) ---
    ("E1102 错误码什么意思", "api_reference.md"),               # 错误码字面命中
    ("qwen-plus 上下文 32k", "troubleshooting.md"),             # 型号关键词
    ("BGE Reranker 升级", "release_notes.md"),                 # 模型名
    # --- 长尾类 (Reranker 见效) ---
    ("VirtualFS 跨 invoke 怎么持久化", "troubleshooting.md"),  # 描述式查询
    ("v2.6.0 加了哪些 RAG 能力", "release_notes.md"),           # 多概念组合
]


if __name__ == "__main__":
    chunks = load_chunks()
    print(f"加载 {len(chunks)} chunks")
    sources = sorted({c.metadata['source'] for c in chunks})
    for s in sources:
        n = sum(1 for c in chunks if c.metadata['source'] == s)
        print(f"  {s}: {n} chunks")
    print(f"\nBM25 jieba 分词测试: {bm25_preprocess('退货政策怎么定的')}")
    print(f"EVAL_QUERIES: {len(EVAL_QUERIES)} queries")

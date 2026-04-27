"""rag_pipeline_helpers — 共享 RAG pipeline 初始化逻辑.

提供 init_vector_store(): 加载 docs → 切分 → 向量化 → 返回 InMemoryVectorStore.
被 02 / 03 共用.
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


def init_vector_store() -> InMemoryVectorStore:
    """加载 docs/*.md, 切分 + 向量化, 返回向量库."""
    docs: list[Document] = []
    for md_file in sorted(_DOCS_DIR.glob("*.md")):
        docs.append(
            Document(
                page_content=md_file.read_text(encoding="utf-8"),
                metadata={"source": md_file.name},
            )
        )

    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vs = InMemoryVectorStore(get_embeddings())
    vs.add_documents(chunks)
    return vs

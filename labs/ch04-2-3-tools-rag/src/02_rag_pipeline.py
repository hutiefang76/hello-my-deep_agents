"""02 · 完整 RAG pipeline — 从 .md 文档到检索回答.

流程:
    docs/*.md → loader → splitter → embedder → InMemoryVectorStore
                                                  ↓
                                      similarity_search
                                                  ↓
                                          retrieved_chunks
                                                  ↓
                                  prompt with context → LLM → answer

教学要点:
    1. TextLoader: 加载单文件
    2. MarkdownTextSplitter: 按 markdown 标题切分 (比 RecursiveCharacterTextSplitter 更适合)
    3. DashScopeEmbeddings: 中文向量化
    4. InMemoryVectorStore: 教学场景, 真实项目用 PgVector
    5. RAG prompt 模板: "基于以下检索到的上下文回答问题"

Run:
    python 02_rag_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402
from langchain_text_splitters import MarkdownTextSplitter  # noqa: E402


DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def load_documents() -> list[Document]:
    """加载 docs/*.md 为 LangChain Document 列表."""
    docs: list[Document] = []
    for md_file in sorted(DOCS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        docs.append(
            Document(
                page_content=text,
                metadata={"source": md_file.name, "category": md_file.stem},
            )
        )
    print(f"  加载 {len(docs)} 个 .md 文档:")
    for d in docs:
        print(f"    - {d.metadata['source']} ({len(d.page_content)} 字符)")
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    """按 markdown 标题切分."""
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"  切分为 {len(chunks)} 个 chunks (chunk_size=500, overlap=50)")
    return chunks


def build_vector_store(chunks: list[Document]) -> InMemoryVectorStore:
    """向量化入库."""
    print("  向量化中... (调用 DashScope embedding API)")
    vs = InMemoryVectorStore(get_embeddings())
    vs.add_documents(chunks)
    print(f"  入库完成, 共 {len(vs.store)} 条向量")
    return vs


def build_rag_chain(vs: InMemoryVectorStore):
    """构造 RAG chain — retrieve → prompt → llm → parse."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是产品客服助手. 严格基于以下检索到的内部资料回答用户问题. "
                "如果资料中没有相关内容, 明确说 '资料中没找到', 不要编.",
            ),
            (
                "human",
                "检索到的资料:\n---\n{context}\n---\n\n用户问题: {question}\n\n请简短回答 (≤ 150 字).",
            ),
        ]
    )

    def retrieve(query: str) -> str:
        chunks = vs.similarity_search(query, k=3)
        return "\n\n".join(
            f"[来源: {c.metadata.get('source', '?')}]\n{c.page_content}" for c in chunks
        )

    llm = get_llm()
    parser = StrOutputParser()

    # LCEL chain
    def rag_invoke(question: str) -> str:
        context = retrieve(question)
        return (prompt | llm | parser).invoke({"context": context, "question": question})

    return rag_invoke, retrieve


def main() -> None:
    print("=" * 60)
    print("Ch4.2.3 · 02 完整 RAG pipeline")
    print("=" * 60)

    print("\n[Step 1] 加载文档")
    docs = load_documents()

    print("\n[Step 2] 切分")
    chunks = split_documents(docs)

    print("\n[Step 3] 向量化 + 入库")
    vs = build_vector_store(chunks)

    print("\n[Step 4] 构造 RAG chain")
    rag_invoke, retrieve = build_rag_chain(vs)

    print("\n[Step 5] 测试问答")

    questions = [
        "退货政策是什么?",
        "qwen-plus 的上下文窗口多大?",
        "如果 PgVector 装不上怎么办?",
        "钻石会员有什么权益?",
        "DASHSCOPE_API_KEY 报错怎么排查?",
    ]

    for q in questions:
        print(f"\n--- Q: {q} ---")
        # 看一眼检索到了啥 (调试用)
        retrieved = retrieve(q)
        first_source = retrieved.split("\n", 1)[0]
        print(f"  [检索] 第 1 chunk 来自: {first_source}")
        # 跑完整 RAG
        answer = rag_invoke(q)
        print(f"  [回答] {answer}")


if __name__ == "__main__":
    main()

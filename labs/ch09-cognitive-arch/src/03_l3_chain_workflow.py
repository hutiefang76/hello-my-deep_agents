"""03 · L3 LLM Chain (Workflow) — 客服工作流.

Chain: Intent Detection → Knowledge Retrieve → Respond Generation

升级理由 (Why upgrade from L2):
    L2 把整个 KB 塞 prompt → KB 大了 token 爆炸
    L3 先判断意图, 再检索相关 KB 条目, 只塞相关的 → 省 token + 更精准

Run:
    python 03_l3_chain_workflow.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from cs_kb import CS_KB  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402


# 用向量库索引 KB
_VS = InMemoryVectorStore(get_embeddings())
_VS.add_documents(
    [Document(page_content=f"{k}: {v}", metadata={"topic": k}) for k, v in CS_KB.items()]
)


class Intent(BaseModel):
    intent: Literal["faq_lookup", "out_of_scope"]
    keywords: list[str] = Field(default_factory=list)


_intent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Classify if user asks FAQ-related (faq_lookup) or other (out_of_scope)."),
        ("human", "{q}"),
    ]
)

_respond_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是客服. 严格基于检索到的 KB 条目回答, ≤ 80 字. 不在 KB 中的请说'转人工'.",
        ),
        ("human", "User question: {q}\n\nRelevant KB:\n{kb}"),
    ]
)


def l3_handle(query: str) -> dict:
    """L3 Chain: intent → retrieve → respond."""
    llm = get_llm(temperature=0.0)
    t0 = time.perf_counter()

    # Step 1: Intent
    intent: Intent = (_intent_prompt | llm.with_structured_output(Intent)).invoke({"q": query})

    # Step 2: Retrieve (只在 faq_lookup 时检索)
    if intent.intent == "faq_lookup":
        retrieved = _VS.similarity_search(query, k=2)
        kb_text = "\n".join(d.page_content for d in retrieved)
    else:
        kb_text = "(no relevant KB)"

    # Step 3: Respond
    answer = (_respond_prompt | llm | StrOutputParser()).invoke(
        {"q": query, "kb": kb_text}
    )

    return {
        "level": "L3",
        "intent": intent.intent,
        "retrieved_topics": [d.metadata.get("topic") for d in (
            _VS.similarity_search(query, k=2) if intent.intent == "faq_lookup" else []
        )],
        "answer": answer,
        "ms": (time.perf_counter() - t0) * 1000,
        "cost": 0.003,
    }


def main() -> None:
    print("=" * 70)
    print("Ch9 · 03 L3 LLM Chain (Workflow) — 客服工作流")
    print("=" * 70)

    queries = [
        "我那双鞋开胶了急用",
        "钻石会员折扣多少?",
        "我能用花呗付吗?",
        "你能帮我查一下我朋友的订单吗?",  # 应判 out_of_scope
        "你们北京次日达吗?",
    ]
    for q in queries:
        result = l3_handle(q)
        print(f"\n  Q: {q}")
        print(f"     intent: {result['intent']}, retrieved: {result['retrieved_topics']}")
        print(f"     A: {result['answer'][:120]}")
        print(f"     {result['ms']:.0f}ms, ~¥{result['cost']}")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - L3 比 L2 节省 token (只塞相关 KB 而非全部)")
    print("  - 意图分流: out_of_scope 直接转人工, 不浪费 LLM")
    print("  - 但 8+ 意图全塞一个 chain → 升级到 L4 Router")


if __name__ == "__main__":
    main()

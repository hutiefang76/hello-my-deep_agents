"""03 · DeepAgent + RAG — 把 RAG 包装成工具.

让 DeepAgent 决定: 这个问题需不需要查知识库? 查哪个查询词?
而不是每个问题都强制走 RAG.

教学要点:
    - 用 @tool 把 retrieve 包成工具
    - 工具描述告诉 LLM "什么场景该用"
    - DeepAgent 自己决定 RAG vs 直答 vs 多次 RAG

Run:
    python 03_deepagent_with_rag.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402

# 复用上一个脚本的 pipeline
from rag_pipeline_helpers import init_vector_store  # noqa: E402

from deepagents import create_deep_agent  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


# 全局向量库 (lazy 初始化)
_VS = None


def _get_vs():
    global _VS
    if _VS is None:
        _VS = init_vector_store()
    return _VS


@tool
def search_knowledge_base(query: str, k: int = 3) -> str:
    """检索内部产品知识库. 适用场景:
    - 用户问退货政策、支付、配送、保修等产品相关问题
    - 用户问技术栈、故障排查
    - 任何需要"内部资料"才能准确回答的问题

    Args:
        query: 检索关键词
        k: 返回前 k 条 (默认 3)
    """
    vs = _get_vs()
    chunks = vs.similarity_search(query, k=k)
    if not chunks:
        return "知识库中未找到相关内容"
    return "\n\n".join(
        f"[来源: {c.metadata.get('source', '?')}]\n{c.page_content}" for c in chunks
    )


SYSTEM_PROMPT = """你是产品客服 + 技术支持助手. 工作流程:
1. 看用户问题, 判断是否需要查知识库
2. 需要查 → 用 search_knowledge_base, 关键词要精准
3. 检索结果不够 → 调整关键词再查 1 次 (最多 2 次)
4. 综合检索结果回答用户 (引用 [来源])

如果用户问的是闲聊或简单问题, 不用查知识库直接答.
回答简短, 100 字以内."""


def main() -> None:
    print("=" * 60)
    print("Ch4.2.3 · 03 DeepAgent + RAG")
    print("=" * 60)

    print("初始化知识库...")
    _ = _get_vs()

    agent = create_deep_agent(
        model=get_llm(),
        tools=[search_knowledge_base],
        system_prompt=SYSTEM_PROMPT,
    )

    test_cases = [
        "你好",                                                          # 闲聊, 不应查 KB
        "退货政策是什么?",                                               # 需要查 KB
        "我们用的什么向量库? 出问题怎么办?",                             # 需要 2 次查 KB
        "1+1 等于几?",                                                   # 简单问题, 不应查 KB
        "qwen-max 和 qwen-long 的上下文区别? 然后告诉我钻石会员权益.",  # 需要 2 次查 KB
    ]

    for msg in test_cases:
        print(f"\n--- 用户: {msg} ---")
        result = agent.invoke(
            {"messages": [HumanMessage(content=msg)]},
            config={"recursion_limit": 15},
        )
        messages = result["messages"]

        kb_calls = sum(
            1
            for m in messages
            for tc in (getattr(m, "tool_calls", None) or [])
            if tc.get("name") == "search_knowledge_base"
        )
        tool_msgs = sum(1 for m in messages if isinstance(m, ToolMessage))

        print(f"  [指标] KB 调用 {kb_calls} 次, tool_msgs {tool_msgs}")
        print(f"  [回复] {messages[-1].content[:200]}")


if __name__ == "__main__":
    main()

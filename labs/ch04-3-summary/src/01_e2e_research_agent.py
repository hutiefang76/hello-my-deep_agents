"""01 · 端到端深度研究 Agent — 集大成 demo.

把前面所有 lab 学的能力组装到一起:
  - 意图识别 (Ch4.2.2): 区分研究请求 vs 闲聊
  - 多层记忆 (Ch4.2.1): 短期 messages + 会话 Checkpointer + 长期 vector
  - 工具 + RAG (Ch4.2.3): web_search + search_kb
  - SubAgent (Ch4.2.4): researcher / writer
  - Planning + FS (Ch4.1): 内置 write_todos + write_file

Run:
    python 01_e2e_research_agent.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "labs" / "ch03-frameworks-compare" / "src"))
sys.path.insert(0, str(REPO_ROOT / "labs" / "ch04-2-3-tools-rag" / "src"))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from common_search import web_search  # noqa: E402
from deepagents import SubAgent, create_deep_agent  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.messages import HumanMessage, ToolMessage  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402
from langgraph.checkpoint.sqlite import SqliteSaver  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from rag_pipeline_helpers import init_vector_store  # noqa: E402


DB_PATH = Path(__file__).parent / "_e2e_memory.db"


# ===== 1. 意图识别 (Ch4.2.2) =====
class Intent(BaseModel):
    category: Literal["research", "qa_kb", "chitchat"]
    confidence: float = Field(ge=0.0, le=1.0)


def classify_intent(message: str) -> Intent:
    llm = get_llm(temperature=0.0)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "意图分类: research=深度研究/调研, qa_kb=问产品 FAQ/技术栈/故障排查, chitchat=闲聊",
            ),
            ("human", "{message}"),
        ]
    )
    return (prompt | llm.with_structured_output(Intent)).invoke({"message": message})


# ===== 2. 长期记忆 (Ch4.2.1) =====
def init_long_term_memory() -> InMemoryVectorStore:
    vs = InMemoryVectorStore(get_embeddings())
    vs.add_documents(
        [
            Document(
                page_content="用户偏好: Java 工程师背景, 关心 LangChain/DeepAgents 在 Java 生态的位置",
                metadata={"user": "default"},
            ),
            Document(
                page_content="用户偏好: 喜欢看代码量对比, 不喜欢空话",
                metadata={"user": "default"},
            ),
        ]
    )
    return vs


# ===== 3. RAG 知识库 (Ch4.2.3) =====
_KB = init_vector_store()  # 复用 Ch4.2.3 的文档


@tool
def search_kb(query: str, k: int = 3) -> str:
    """检索内部产品知识库 (退货政策/技术栈/故障排查).

    Args:
        query: 搜索关键词
        k: top-k
    """
    chunks = _KB.similarity_search(query, k=k)
    if not chunks:
        return "知识库中未找到相关内容"
    return "\n\n".join(
        f"[来源: {c.metadata.get('source')}]\n{c.page_content}" for c in chunks
    )


# ===== 4. SubAgent (Ch4.2.4) =====
researcher_agent = SubAgent(
    name="researcher",
    description="联网调研专家. 当需要外部资料/最新信息时派给我.",
    system_prompt="你是研究员, 用 web_search 搜 1-2 次, 列 3-5 条要点.",
    tools=[web_search],
)

writer_agent = SubAgent(
    name="writer",
    description="技术写手. 当需要把素材整理成正式 markdown 时派给我.",
    system_prompt="你是写手, 把素材整成 ## 一级 + ### 二级 标题的 markdown, 200-400 字.",
)


# ===== 5. 主 Agent + 路由 =====
def build_research_agent(checkpointer):
    """研究意图: 用 SubAgent + Planning + FS"""
    return create_deep_agent(
        model=get_llm(),
        tools=[web_search, search_kb],
        system_prompt=(
            "你是深度研究助手 (项目经理风格). 收到研究问题:\n"
            "1. 用 write_todos 列计划 (3-5 步)\n"
            "2. 派 researcher 联网调研 + 派 search_kb 查内部知识库\n"
            "3. 派 writer 整理成 markdown\n"
            "4. write_file 存到 'final_report.md'\n"
            "5. 给用户一句话总结"
        ),
        subagents=[researcher_agent, writer_agent],
        checkpointer=checkpointer,
    )


def build_qa_agent(checkpointer):
    """KB 问答意图: 用 RAG"""
    return create_deep_agent(
        model=get_llm(),
        tools=[search_kb],
        system_prompt=(
            "你是产品助手. 用 search_kb 查内部资料, 引用 [来源] 简短回答 (≤ 100 字)."
        ),
        checkpointer=checkpointer,
    )


def build_chitchat_agent(checkpointer):
    """闲聊意图: 不用工具"""
    return create_deep_agent(
        model=get_llm(),
        tools=[],
        system_prompt="你是友好客服, 简短回应闲聊, 不用工具.",
        checkpointer=checkpointer,
    )


# ===== 6. 端到端调用 =====
def chat(user_msg: str, thread_id: str, long_term: InMemoryVectorStore) -> dict:
    """端到端处理一条用户消息."""
    # Step 1: 意图分类
    intent = classify_intent(user_msg)
    print(f"  [意图] {intent.category} (conf={intent.confidence:.2f})")

    # Step 2: 长期记忆检索
    relevant = long_term.similarity_search(user_msg, k=2)
    if relevant:
        memory_hint = "; ".join(d.page_content for d in relevant)
        print(f"  [长期记忆] {memory_hint[:80]}...")
    else:
        memory_hint = ""

    # Step 3: 按意图选 Agent
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    if intent.category == "research":
        agent = build_research_agent(checkpointer)
    elif intent.category == "qa_kb":
        agent = build_qa_agent(checkpointer)
    else:
        agent = build_chitchat_agent(checkpointer)

    # Step 4: 注入长期记忆 + 调用
    messages = []
    if memory_hint:
        messages.append(HumanMessage(content=f"[用户背景]: {memory_hint}"))
    messages.append(HumanMessage(content=user_msg))

    # 研究路径需要的步骤多 (SubAgent 派发 + Planning + FS), 拉到 50
    result = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 50},
    )

    msgs = result["messages"]
    files = result.get("files", {})

    tool_calls_made: list[str] = []
    for m in msgs:
        for tc in getattr(m, "tool_calls", []) or []:
            tool_calls_made.append(tc.get("name", ""))

    conn.close()

    return {
        "intent": intent.category,
        "tools_used": sorted(set(tool_calls_made)),
        "tool_msgs": sum(1 for m in msgs if isinstance(m, ToolMessage)),
        "files": list(files.keys()),
        "reply": msgs[-1].content,
        "files_data": files,
    }


def main() -> None:
    print("=" * 60)
    print("Ch4.3 · 01 端到端深度研究 Agent (集大成)")
    print("=" * 60)

    if DB_PATH.exists():
        DB_PATH.unlink()

    long_term = init_long_term_memory()
    print(f"长期记忆初始化: {len(long_term.store)} 条")
    print(f"知识库初始化: {len(_KB.store)} 条 chunks")

    test_cases = [
        ("default-2026-04-27", "你好"),
        ("default-2026-04-27", "退货政策是什么? "),
        ("default-2026-04-27", "深度研究: LangChain 1.0 比 0.3 有哪些重要变化?"),
    ]

    for thread, msg in test_cases:
        print(f"\n--- thread={thread} 用户: {msg} ---")
        try:
            out = chat(msg, thread, long_term)
            print(f"  [结果] intent={out['intent']}, "
                  f"tools_used={out['tools_used']}, "
                  f"files={out['files']}")
            print(f"  [回复] {out['reply'][:200]}")
            if "final_report.md" in out["files_data"]:
                print(f"\n  [终稿] {out['files_data']['final_report.md'][:300]}")
        except Exception as e:
            # 网络抖动 / SSL EOF 等不阻塞整体演示
            print(f"  [ERR] {type(e).__name__}: {str(e)[:120]}")
            print(f"  [说明] 网络抖动可能触发, 重跑或换网即可. 本 case 跳过.")


if __name__ == "__main__":
    main()

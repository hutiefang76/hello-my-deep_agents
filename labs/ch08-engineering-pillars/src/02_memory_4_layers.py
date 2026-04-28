"""02 · Memory 4 Layers — OpenAI 分层记忆模型.

OpenAI Guide: "Memory ≠ vector DB: use layered memory."

4 Layers (4 层):
    1. Working   工作记忆: 当前对话上下文 (messages 列表)
    2. Summary   摘要记忆: 历史会话浓缩 (避免 token 爆)
    3. Artifacts 物件记忆: 中间产物 (DeepAgents virtual FS — 上一轮课的核心)
    4. Long-term 长期记忆: 用户偏好, 跨会话持久 (vector store)

vs Ch4.2.1 (我之前的多层记忆 lab):
    - Ch4.2.1 cover 了 Working + Long-term 但漏了 **Artifacts 这一层**
    - 而 Artifacts = DeepAgents virtual FS = 真实生产 Agent 的核心
    - 本章把这一层补上 + 加 Summary 层

Run:
    python 02_memory_4_layers.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402


# ============================================================
# 4 层 Memory 容器
# ============================================================


@dataclass
class FourLayerMemory:
    """OpenAI 分层记忆模型实现."""

    # Layer 1: Working — 当前对话 messages (短)
    working: list = field(default_factory=list)

    # Layer 2: Summary — 历史浓缩
    summary: str = ""

    # Layer 3: Artifacts — 中间产物 (类 DeepAgents virtual FS)
    artifacts: dict[str, str] = field(default_factory=dict)

    # Layer 4: Long-term — 用户偏好/事实, 向量化检索
    long_term: InMemoryVectorStore | None = None

    def __post_init__(self):
        if self.long_term is None:
            self.long_term = InMemoryVectorStore(get_embeddings())

    # ----- Working 操作 -----
    def add_working(self, msg) -> None:
        self.working.append(msg)

    def get_working(self, last_n: int = 6) -> list:
        return self.working[-last_n:]

    # ----- Summary 操作 -----
    def update_summary(self, llm) -> None:
        """把老消息总结进 summary, 然后清掉 working 老消息."""
        if len(self.working) < 8:
            return  # 还不够长

        old = self.working[:-4]  # 保留最近 4 条
        old_text = "\n".join(getattr(m, "content", str(m))[:120] for m in old)

        result = llm.invoke(
            f"Summarize this conversation history in 2 sentences:\n{old_text}\n\n"
            f"Previous summary: {self.summary}"
        )
        self.summary = result.content
        self.working = self.working[-4:]  # 截断

    # ----- Artifacts 操作 -----
    def write_artifact(self, name: str, content: str) -> None:
        self.artifacts[name] = content

    def read_artifact(self, name: str) -> str | None:
        return self.artifacts.get(name)

    def list_artifacts(self) -> list[str]:
        return list(self.artifacts.keys())

    # ----- Long-term 操作 -----
    def remember_long_term(self, fact: str, metadata: dict) -> None:
        self.long_term.add_documents([Document(page_content=fact, metadata=metadata)])

    def recall_long_term(self, query: str, k: int = 3) -> list[str]:
        docs = self.long_term.similarity_search(query, k=k)
        return [d.page_content for d in docs]

    # ----- 综合 prompt 构造 -----
    def build_prompt(self, user_query: str, last_working_n: int = 4) -> list:
        """构造 prompt — 把 4 层记忆都用上."""
        msgs = []

        # Layer 4: 长期记忆检索 (相关偏好)
        long_term_facts = self.recall_long_term(user_query, k=2)
        if long_term_facts:
            msgs.append(
                SystemMessage(content="User profile: " + "; ".join(long_term_facts))
            )

        # Layer 2: Summary
        if self.summary:
            msgs.append(SystemMessage(content=f"Conversation summary: {self.summary}"))

        # Layer 3: 当前 artifacts 列表
        if self.artifacts:
            msgs.append(
                SystemMessage(
                    content=f"Available artifacts: {self.list_artifacts()}"
                )
            )

        # Layer 1: 最近的 Working messages
        msgs.extend(self.get_working(last_working_n))

        # Current query
        msgs.append(HumanMessage(content=user_query))
        return msgs


def demo_long_session() -> None:
    """模拟长会话, 4 层 memory 协同工作."""
    print("\n--- 长会话 demo: 客服处理一个复杂投诉 (4 轮+) ---")
    mem = FourLayerMemory()
    llm = get_llm()

    # 预填长期记忆 (用户画像)
    mem.remember_long_term(
        "VIP 客户 Alice, 偏好快速解决, 不喜欢客套话",
        {"user": "alice", "type": "preference"},
    )
    mem.remember_long_term(
        "Alice 上次投诉是 2026-04-01 关于物流慢, 已退款补偿",
        {"user": "alice", "type": "history"},
    )
    print(f"  长期记忆预填: {len(mem.long_term.store)} 条")

    # 第 1 轮
    q1 = "我又来了, 这次是鞋子的问题, 穿一周开胶了"
    msgs1 = mem.build_prompt(q1, last_working_n=0)
    print(f"\n  [Round 1] 用户: {q1}")
    print(f"    Prompt 含: {len(msgs1)} 条 messages (含 long-term + summary + working)")
    r1 = llm.invoke(msgs1)
    print(f"    AI: {r1.content[:80]}...")
    mem.add_working(HumanMessage(content=q1))
    mem.add_working(r1)

    # 第 2 轮 — 用 artifacts 记录工单
    q2 = "我要订单号 O20260427 全额退款"
    print(f"\n  [Round 2] 用户: {q2}")
    mem.write_artifact(
        "ticket_001.md", f"Customer: Alice\nIssue: 鞋子开胶\nOrder: O20260427\nResolution: pending"
    )
    print(f"    Artifact 写入: ticket_001.md ({len(mem.artifacts)} 个)")
    r2 = llm.invoke(mem.build_prompt(q2, last_working_n=2))
    print(f"    AI: {r2.content[:80]}...")
    mem.add_working(HumanMessage(content=q2))
    mem.add_working(r2)

    # 第 3-5 轮
    for i, q in enumerate(
        [
            "好, 那退款多久到账?",
            "我用支付宝付的, 退到原渠道吗?",
            "能不能补偿 2 张优惠券?",
            "好, 谢谢. 顺便问一下, 我之前那次物流问题最后赔了多少?",
        ],
        start=3,
    ):
        print(f"\n  [Round {i}] 用户: {q[:40]}...")
        msgs = mem.build_prompt(q, last_working_n=4)
        r = llm.invoke(msgs)
        mem.add_working(HumanMessage(content=q))
        mem.add_working(r)

        # 第 5 轮触发 summary 压缩
        if len(mem.working) >= 8:
            mem.update_summary(llm)
            print(f"    [触发摘要压缩] working 截断到 {len(mem.working)} 条")
            print(f"    Summary: {mem.summary[:80]}...")

    print("\n  --- 最终 Memory 状态 ---")
    print(f"    Layer 1 Working:     {len(mem.working)} messages")
    print(f"    Layer 2 Summary:     '{mem.summary[:80]}...'")
    print(f"    Layer 3 Artifacts:   {mem.list_artifacts()}")
    print(f"    Layer 4 Long-term:   {len(mem.long_term.store)} 条事实")


def main() -> None:
    print("=" * 70)
    print("Ch8 · 02 Memory 4 Layers — OpenAI 分层记忆")
    print("=" * 70)

    demo_long_session()

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  Layer 1 Working — 4-10 messages 窗口, 当前上下文")
    print("  Layer 2 Summary — 当 working 超长时压缩, 防 token 爆")
    print("  Layer 3 Artifacts — 中间产物 (工单/草稿/报告), DeepAgents virtual FS 同款")
    print("  Layer 4 Long-term — 跨会话偏好/历史, 向量检索")
    print()
    print("OpenAI 原文: 'Memory ≠ vector DB: use layered memory.'")
    print("中文: '记忆不等于向量库, 用分层记忆.'")
    print("=" * 70)


if __name__ == "__main__":
    main()

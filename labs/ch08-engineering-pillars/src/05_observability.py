"""05 · Observability — Trace + Cost + 语义缓存.

生产级 Agent 必须具备:
    1. Trace 链路追踪 (LangSmith pattern, 或自研)
    2. Cost 成本追踪 (token 计数 + 单价计算)
    3. Semantic Cache 语义缓存 (相似 query 复用结果, 省 token)

vs LangSmith / Langfuse 等托管平台:
    - 这里实现 minimal pattern, 教学用
    - 真实生产可直接接 LangSmith (一行 LANGSMITH_TRACING=true)

Run:
    python 05_observability.py
"""

from __future__ import annotations

import hashlib
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from common.llm import get_embeddings, get_llm  # noqa: E402
from langchain_core.documents import Document  # noqa: E402
from langchain_core.vectorstores import InMemoryVectorStore  # noqa: E402


# ============================================================
# 1. Cost Tracker — 成本追踪
# ============================================================


# 阿里云通义千问定价 (2026-04, 元/1k tokens)
_PRICING = {
    "qwen-turbo": {"input": 0.001, "output": 0.002},
    "qwen-plus": {"input": 0.004, "output": 0.012},
    "qwen-max": {"input": 0.020, "output": 0.060},
}


@dataclass
class CostTracker:
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_yuan: float = 0.0
    call_count: int = 0
    by_model: dict = field(default_factory=dict)

    def record(self, model: str, input_tokens: int, output_tokens: int):
        price = _PRICING.get(model, _PRICING["qwen-plus"])
        cost = (input_tokens * price["input"] + output_tokens * price["output"]) / 1000

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_yuan += cost
        self.call_count += 1
        self.by_model.setdefault(model, {"calls": 0, "cost": 0.0})
        self.by_model[model]["calls"] += 1
        self.by_model[model]["cost"] += cost

    def report(self) -> str:
        lines = [
            f"  总调用: {self.call_count}",
            f"  Input tokens:  {self.total_input_tokens:,}",
            f"  Output tokens: {self.total_output_tokens:,}",
            f"  总成本:        ¥{self.total_cost_yuan:.4f}",
            f"  按模型:",
        ]
        for m, d in self.by_model.items():
            lines.append(f"    {m}: {d['calls']} 次, ¥{d['cost']:.4f}")
        return "\n".join(lines)


# ============================================================
# 2. Trace Tracker — 简化 LangSmith pattern
# ============================================================


@dataclass
class TraceEvent:
    timestamp: float
    span_type: str  # LLM / TOOL / CACHE_HIT / CACHE_MISS
    name: str
    duration_ms: float
    metadata: dict = field(default_factory=dict)


@dataclass
class Tracer:
    events: list = field(default_factory=list)

    def emit(self, span_type: str, name: str, duration_ms: float, **metadata):
        self.events.append(
            TraceEvent(
                timestamp=time.time(),
                span_type=span_type,
                name=name,
                duration_ms=duration_ms,
                metadata=metadata,
            )
        )

    def summary(self) -> dict:
        by_type: dict[str, list] = {}
        for e in self.events:
            by_type.setdefault(e.span_type, []).append(e.duration_ms)
        return {
            t: {"count": len(durs), "total_ms": sum(durs), "avg_ms": sum(durs) / len(durs)}
            for t, durs in by_type.items()
        }


# ============================================================
# 3. Semantic Cache — 语义缓存
# ============================================================


@dataclass
class SemanticCache:
    """语义缓存 — 相似 query 命中 cache, 省 LLM 调用."""

    threshold: float = 0.85  # 余弦相似度阈值
    store: InMemoryVectorStore = None  # type: ignore
    cache_data: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.store is None:
            self.store = InMemoryVectorStore(get_embeddings())

    def lookup(self, query: str) -> str | None:
        """查相似 query."""
        if not self.cache_data:
            return None
        # 简化: 用 similarity_search 取最相近, 实际应该看相似度分
        docs = self.store.similarity_search_with_score(query, k=1) if hasattr(
            self.store, "similarity_search_with_score"
        ) else None

        if docs:
            doc, score = docs[0]
            # InMemoryVectorStore 的 score 是距离 (越小越相似)
            # 简化判断
            if score < (1.0 - self.threshold):
                return self.cache_data.get(doc.page_content)
        return None

    def put(self, query: str, answer: str):
        self.store.add_documents([Document(page_content=query)])
        self.cache_data[query] = answer


# ============================================================
# 集大成: 带 Trace + Cost + Cache 的 LLM 调用
# ============================================================


class InstrumentedLLM:
    """包装 LLM, 加 trace + cost + cache."""

    def __init__(self, model: str = "qwen-plus"):
        self.llm = get_llm(model=model)
        self.model = model
        self.tracer = Tracer()
        self.cost = CostTracker()
        self.cache = SemanticCache(threshold=0.85)

    def invoke(self, query: str, use_cache: bool = True) -> str:
        # 1. Cache lookup
        if use_cache:
            t0 = time.perf_counter()
            cached = self.cache.lookup(query)
            cache_ms = (time.perf_counter() - t0) * 1000
            if cached is not None:
                self.tracer.emit("CACHE_HIT", "semantic_cache", cache_ms, query=query[:50])
                return cached
            self.tracer.emit("CACHE_MISS", "semantic_cache", cache_ms, query=query[:50])

        # 2. Real LLM call
        t0 = time.perf_counter()
        response = self.llm.invoke(query)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # 3. Cost (估算 — 真实场景从 response.usage_metadata 取)
        in_tokens = len(query) // 2  # 粗估
        out_tokens = len(response.content) // 2
        self.cost.record(self.model, in_tokens, out_tokens)
        self.tracer.emit("LLM", self.model, elapsed_ms, in_tokens=in_tokens, out_tokens=out_tokens)

        # 4. Put in cache
        if use_cache:
            self.cache.put(query, response.content)

        return response.content


def main() -> None:
    print("=" * 70)
    print("Ch8 · 05 Observability — Trace + Cost + Semantic Cache")
    print("=" * 70)

    llm = InstrumentedLLM(model="qwen-plus")

    queries = [
        "你好",
        "你们的退货政策是什么?",
        "你们退货政策怎么规定的?",  # 与上一条语义相似 → 期望命中 cache
        "qwen-plus 的上下文窗口多大?",
        "qwen-plus 的 context 窗口大小?",  # 期望命中 cache
        "钻石会员有什么权益?",
    ]

    print(f"\n跑 {len(queries)} 个 query:\n")
    for i, q in enumerate(queries, 1):
        print(f"  Query {i}: {q}")
        t0 = time.perf_counter()
        result = llm.invoke(q)
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"    → {result[:80]}... ({elapsed:.0f}ms)")

    print("\n" + "=" * 70)
    print("📊 Cost Report")
    print(llm.cost.report())

    print("\n📈 Trace Summary")
    summary = llm.tracer.summary()
    for span_type, stats in summary.items():
        print(
            f"  {span_type:<12}  count={stats['count']:>3}  "
            f"total={stats['total_ms']:.0f}ms  avg={stats['avg_ms']:.0f}ms"
        )

    cache_hits = summary.get("CACHE_HIT", {}).get("count", 0)
    cache_misses = summary.get("CACHE_MISS", {}).get("count", 0)
    if cache_hits + cache_misses > 0:
        hit_rate = cache_hits / (cache_hits + cache_misses) * 100
        print(f"\n  Cache 命中率: {hit_rate:.0f}% ({cache_hits}/{cache_hits + cache_misses})")

    print("\n" + "=" * 70)
    print("观察 (Observations):")
    print("  - Cost: 简单 query 单价低, 但累积是真金白银")
    print("  - Cache: 客服场景命中率 30-50% 常见 (FAQ 高度重复)")
    print("  - Trace: 7 span types 一目了然 LLM/Tool/Cache 各占多少时间")
    print("  - 接 LangSmith: 设 LANGSMITH_TRACING=true 即可托管, 不用自己实现")
    print("=" * 70)


if __name__ == "__main__":
    main()

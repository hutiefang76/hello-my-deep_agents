"""06 · async / await — 异步编程入门.

对照:
    Java                                Python
    ──────                              ──────
    CompletableFuture<T>                Coroutine[Any, Any, T]  (async def 返回值)
    .thenApply / .thenCompose           await
    @Async + ExecutorService            asyncio + asyncio.create_task
    Future<T>.get()                     await coro
    parallelStream                      asyncio.gather

为什么 LLM 应用必须懂 async:
    LLM 调用是 I/O 密集型 (等网络), 串行调用 5 个工具要 5x 的时间,
    用 asyncio.gather 并发可以拉到接近 1x. LangChain / LangGraph 全部是 async-first.

Run:
    python 06_async_basics.py
"""

from __future__ import annotations

import asyncio
import time


async def fake_llm_call(prompt: str, latency_sec: float = 1.0) -> str:
    """模拟一次 LLM 调用 — 实际是 await asyncio.sleep, 这是 I/O 等待的代名词."""
    await asyncio.sleep(latency_sec)  # 关键: await 让出执行权, 不阻塞别人
    return f"[LLM 回复] {prompt}"


async def serial_demo() -> None:
    """串行: 依次 await, 总耗时 = sum(各次)."""
    t0 = time.perf_counter()
    r1 = await fake_llm_call("question 1", 1.0)
    r2 = await fake_llm_call("question 2", 1.0)
    r3 = await fake_llm_call("question 3", 1.0)
    elapsed = time.perf_counter() - t0
    print(f"  串行: {elapsed:.2f}s → {[r1, r2, r3]}")


async def parallel_demo() -> None:
    """并行: asyncio.gather 同时发, 总耗时 ≈ max(各次)."""
    t0 = time.perf_counter()
    r1, r2, r3 = await asyncio.gather(
        fake_llm_call("question 1", 1.0),
        fake_llm_call("question 2", 1.0),
        fake_llm_call("question 3", 1.0),
    )
    elapsed = time.perf_counter() - t0
    print(f"  并行: {elapsed:.2f}s → {[r1, r2, r3]}")


async def task_with_timeout() -> None:
    """超时控制 — 类似 Java CompletableFuture.orTimeout()."""
    try:
        result = await asyncio.wait_for(
            fake_llm_call("slow question", 3.0),
            timeout=1.0,
        )
        print(f"  result: {result}")
    except asyncio.TimeoutError:
        print("  [TIMEOUT] 超时 (预期行为, 1s 超时但任务要 3s)")


async def cancelled_task() -> None:
    """取消任务 — Python 任务可以中途取消."""
    task = asyncio.create_task(fake_llm_call("background", 5.0))
    await asyncio.sleep(0.1)  # 让 task 跑一会
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("  [CANCELLED] 任务已取消")


async def main() -> None:
    print("=== async / await 演示 ===\n")

    print("--- 1. 串行 vs 并行 ---")
    await serial_demo()
    await parallel_demo()

    print("\n--- 2. 超时控制 ---")
    await task_with_timeout()

    print("\n--- 3. 任务取消 ---")
    await cancelled_task()

    print("\n--- 关键认知 ---")
    print("  - async def 不是多线程, 是协程 (单线程切换)")
    print("  - await 把执行权让给 event loop, 等结果时不阻塞")
    print("  - asyncio.gather() 是并发的关键, 比 ThreadPoolExecutor 轻量")
    print("  - LangChain 大量用 ainvoke / astream, 学会 async 才能高效用")


if __name__ == "__main__":
    # asyncio.run 启动 event loop, 类似 Java 的 main 启动 JVM
    asyncio.run(main())

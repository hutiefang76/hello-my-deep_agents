import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

/**
 * 等价 Python: src/06_async_basics.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Python                              Java 8 老写法                      JDK 23 新写法
 *   ──────                              ─────────────                       ──────────────
 *   async def f()                       CompletableFuture&lt;T&gt;                同左 + Virtual Threads
 *   await f()                           future.get() / .thenApply           future.join() / .get()
 *   asyncio.gather(*futures)            CompletableFuture.allOf(...)        同左
 *   asyncio.create_task(f)              CompletableFuture.supplyAsync(...)  Thread.startVirtualThread
 *   asyncio.wait_for(f, timeout)        future.orTimeout(d) (JDK 9+)        future.get(d, unit)
 *   task.cancel()                       future.cancel(true)                 同左
 *   asyncio.run(main())                 main() 直接调 future.get()          main() 直接调
 * </pre>
 *
 * <p>JDK 23 关键升级 (vs Java 8):
 * <ul>
 *   <li>JEP 444 (Java 21): Virtual Threads stable — 一个线程 = 一个轻量级协程, 等价 Python coroutine</li>
 *   <li>{@code Thread.startVirtualThread(runnable)} 等价 {@code asyncio.create_task(coro)}</li>
 *   <li>结构化并发 (JEP 480, JDK 23 第三次预览) 让 try-with-resources 管理多任务</li>
 *   <li>{@code CompletableFuture.orTimeout(Duration)} (JDK 9+) — 超时控制</li>
 * </ul>
 *
 * <p>为什么 LLM 应用必须懂 async (Python 视角) / Virtual Threads (Java 视角):
 * <p>LLM 调用是 I/O 密集型 (等网络). 串行 5 次 = 5x 延迟; 并发 = 1x. LangChain4j /
 * Spring AI 的 future-based API 等价 LangChain 的 ainvoke/astream.
 */
class AsyncBasics {

    /** 模拟 LLM 调用 — 等价 Python 的 await asyncio.sleep + return. */
    static String fakeLlmCall(final String prompt, final long latencyMs) {
        try {
            Thread.sleep(latencyMs); // 模拟 I/O 等待
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }
        return "[LLM 回复] " + prompt;
    }

    // ===== 1. 串行 demo — 等价 Python 的依次 await =====
    static void serialDemo() {
        final var t0 = Instant.now();
        final var r1 = fakeLlmCall("question 1", 1000);
        final var r2 = fakeLlmCall("question 2", 1000);
        final var r3 = fakeLlmCall("question 3", 1000);
        final var elapsed = Duration.between(t0, Instant.now()).toMillis();
        System.out.println("  串行: %dms → [%s, %s, %s]".formatted(elapsed, r1, r2, r3));
    }

    // ===== 2. 并行 demo — JDK 21+ Virtual Threads (等价 asyncio.gather) =====
    static void parallelDemoVirtualThreads() throws InterruptedException, ExecutionException {
        final var t0 = Instant.now();
        // Virtual Thread 是 JDK 21+ 的轻量级线程, 一台机器可启百万个 (普通 Thread 只能启数千)
        // 这是 Python coroutine 在 JVM 上的最直接对应
        // 用 Virtual Thread 作为 executor — 每个任务跑在独立的 vthread 上
        final java.util.concurrent.Executor vtExec = r -> Thread.startVirtualThread(r);
        final var f1 = CompletableFuture.supplyAsync(() -> fakeLlmCall("question 1", 1000), vtExec);
        final var f2 = CompletableFuture.supplyAsync(() -> fakeLlmCall("question 2", 1000), vtExec);
        final var f3 = CompletableFuture.supplyAsync(() -> fakeLlmCall("question 3", 1000), vtExec);

        // CompletableFuture.allOf 等价 asyncio.gather
        CompletableFuture.allOf(f1, f2, f3).get();
        final var results = List.of(f1.get(), f2.get(), f3.get());
        final var elapsed = Duration.between(t0, Instant.now()).toMillis();
        System.out.println("  并行 (Virtual Threads): %dms → %s".formatted(elapsed, results));
    }

    // ===== 3. 超时控制 — 等价 Python asyncio.wait_for =====
    static void timeoutDemo() {
        final java.util.concurrent.Executor vtExec = r -> Thread.startVirtualThread(r);
        final var future = CompletableFuture.supplyAsync(
                () -> fakeLlmCall("slow question", 3000),
                vtExec);
        try {
            // get(timeout, unit) 等价 await asyncio.wait_for(coro, timeout=1.0)
            final var result = future.get(1, TimeUnit.SECONDS);
            System.out.println("  result: " + result);
        } catch (TimeoutException e) {
            System.out.println("  [TIMEOUT] 超时 (预期行为, 1s 超时但任务要 3s)");
            future.cancel(true);
        } catch (InterruptedException | ExecutionException e) {
            System.out.println("  [ERROR] " + e.getMessage());
        }
    }

    // ===== 4. 任务取消 — 等价 Python task.cancel() =====
    static void cancelDemo() throws InterruptedException {
        final java.util.concurrent.Executor vtExec = r -> Thread.startVirtualThread(r);
        final var future = CompletableFuture.supplyAsync(
                () -> fakeLlmCall("background", 5000),
                vtExec);
        Thread.sleep(100); // 让任务跑一会
        final var cancelled = future.cancel(true);
        System.out.println("  [CANCELLED] cancel() 返回: " + cancelled);
    }

    public static void main(final String[] args) throws Exception {
        // pattern matching switch — 根据参数选 demo (JDK 21+ stable)
        final var mode = args.length > 0 ? args[0] : "all";
        final var label = switch (mode) {
            case "serial" -> "仅串行";
            case "parallel" -> "仅并行";
            case "timeout" -> "仅超时";
            case "cancel" -> "仅取消";
            default -> "全部";
        };
        System.out.println("=== async / Virtual Threads 演示 (mode=" + label + ") ===\n");

        if ("all".equals(mode) || "serial".equals(mode)) {
            System.out.println("--- 1. 串行 ---");
            serialDemo();
        }
        if ("all".equals(mode) || "parallel".equals(mode)) {
            System.out.println("--- 2. 并行 (Virtual Threads) ---");
            parallelDemoVirtualThreads();
        }
        if ("all".equals(mode) || "timeout".equals(mode)) {
            System.out.println("\n--- 3. 超时控制 ---");
            timeoutDemo();
        }
        if ("all".equals(mode) || "cancel".equals(mode)) {
            System.out.println("\n--- 4. 任务取消 ---");
            cancelDemo();
        }

        final var summary = """

                --- 关键认知 ---
                  - Python async def 是协程, 单线程切换, 由 event loop 调度
                  - Java 21+ Virtual Threads 是 JVM 调度的轻量级线程, 阻塞 I/O 时自动让出 carrier
                  - 两者目标相同: 让"看起来阻塞的代码"实际是非阻塞的
                  - asyncio.gather ↔ CompletableFuture.allOf
                  - asyncio.wait_for ↔ future.get(timeout, unit)
                  - LangChain4j / Spring AI 也是 future-based, 学会异步才能高效用
                """;
        System.out.println(summary);
    }
}

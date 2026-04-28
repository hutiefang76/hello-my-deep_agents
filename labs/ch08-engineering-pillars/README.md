# Ch 8 · Engineering Four Pillars — 工程化四件套

> **主线对应** (Mainline): Chase 5 级中的 **L5 (Autonomous Agent) — 从原型到生产**
>
> **大佬出处** (Reference): OpenAI *"A Practical Guide to Building Agents"* (34p PDF, 2025-04-17)
>
> **OpenAI 原文** (English):
> *"In production, an agent is not a prompt — it's a distributed system where the LLM happens to be the planner/executor. Define strict tool contracts, make state transitions deterministic, add trace-level observability, and ship evaluation in CI."*
>
> **中文翻译**：在生产环境，Agent 不是一个 prompt — 它是一个**分布式系统**，LLM 恰好是其中的规划/执行器. 定义严格工具契约、让状态转换确定化、加 trace 级可观测性、把评估纳入 CI.

---

## 四件套全景图 (Four Pillars Overview)

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ ① Tools        │ ② Memory       │ ③ Guardrails   │ ④ Evaluation    │
│   工具          │   记忆          │   护栏          │   评估           │
├────────────────┼────────────────┼────────────────┼────────────────┤
│ Contract 契约   │ Working 工作    │ LLM-based      │ Trajectory 轨迹 │
│ Idempotent 幂等 │ Summary 摘要    │ Rules 规则     │ LLM-as-judge   │
│ Timeout 超时    │ Artifacts 物件  │ Moderation API │ Online/Offline │
│ Circuit Breaker │ Long-term 长期  │                │ 7 Span Types    │
│  熔断           │                │                │                 │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

---

## 学完能力 (Learning Outcomes)

- 写出**生产级工具** (含 contract/timeout/circuit breaker, 不是 demo 级 mock)
- 理解 **Memory 4 层** (Working/Summary/**Artifacts**/Long-term) 各自的用途
- 部署 **Guardrails 三栈** (LLM-based + Rules-based + Moderation API)
- 做 **Trajectory Evaluation** (轨迹评估, 不是终态评估)
- 接 **Observability** (Trace/Metrics/Cost) — 简化版 LangSmith pattern

---

## 脚本列表

| 脚本 | 内容 | 双业务案例 |
|---|---|---|
| `01_tool_engineering.py` | Tool 4 件套: Contract/Idempotent/Timeout/Circuit Breaker | 客服: 真接外部 API / 数分: SQL 工具 |
| `02_memory_4_layers.py` | Working / Summary / **Artifacts** / Long-term | 客服 long-running session |
| `03_guardrails_3_stacks.py` | LLM-based + Rules + Moderation 三栈 | 客服: 输入毒性 + 输出敏感词 + 越权请求 |
| `04_trajectory_eval.py` | 轨迹评估 + 7 span types + LLM-as-judge | 客服 / 数分 双业务 trace 评估 |
| `05_observability.py` | Trace + Cost tracking + 语义缓存 | 跨业务通用 |

## 一键验证

```bash
bash verify.sh
```

## OpenAI 原文金句 (Quotes)

> EN: *"Memory ≠ vector DB: use layered memory (working, summaries, artifacts, long-term preferences)."*
>
> 中文：记忆不等于向量库. 用**分层记忆** (工作/摘要/物件/长期偏好).

> EN: *"Evaluate full trajectories, not just the final message: tool choice correctness, argument validity, step count, time/cost, and policy compliance."*
>
> 中文：评估**完整轨迹**, 不只是最终消息: 工具选择正确性 / 参数有效性 / 步数 / 时间-成本 / 策略合规.

> EN: *"Guardrails act in real time, preventing unsafe or non-compliant behavior before responses reach the user. Evaluations act in batches, testing large sets of prompts to measure reliability over time."*
>
> 中文：**Guardrails 实时**防止不安全行为到达用户. **Evaluations 批量**测试可靠性随时间变化.

## 7 Span Types — Observability Standard

| Span Type | 中文 | 用途 |
|---|---|---|
| **CHAIN** | 链 | 顶层 Agent 调用链 |
| **RETRIEVER** | 检索器 | RAG 检索 span |
| **RERANKER** | 重排器 | 二次精排 |
| **LLM** | LLM 调用 | 单次 LLM 请求 |
| **EMBEDDING** | 向量化 | embedding 生成 |
| **TOOL** | 工具 | 单次工具调用 |
| **AGENT** | 智能体 | Agent 决策 step |

## 下一步

学完工程化四件套 → 进 [Ch 9 Cognitive Architecture 实战](../ch09-cognitive-arch/) 真业务从 L1 演化到 L5.

## 参考

- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

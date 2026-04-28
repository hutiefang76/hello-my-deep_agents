# Erik Schluntz & Barry Zhang (Anthropic) · Building Effective Agents · 5 Patterns

> Anthropic 应用 AI 团队 · 2024-12 发表的 *Building Effective Agents* 是**整个 2025 年 Agent 圈最被引用的实战指南**
> 影响力: 直接影响 LangGraph / DeepAgents / Claude Code 的设计哲学

---

## 1. 核心命题: Workflow vs Agent 二分法

> *"Workflows are systems where LLMs and tools are orchestrated through **predefined code paths**. In contrast, agents are systems where LLMs **dynamically direct their own processes** and tool usage."*

**中文**:
- **Workflow** = LLM + 工具 按**预定义代码路径**编排
- **Agent** = LLM **动态决定**自己的流程和工具

**为什么重要**: 这一刀切清楚后，市面上所有"Agent 框架"都能被分类——大多数其实是 Workflow，伪装成 Agent。

---

## 2. 五大 Workflow Pattern (5 Patterns)

| # | Pattern | 中文 | 何时用 |
|---|---|---|---|
| 1 | **Prompt Chaining** | 提示词串联 | 任务可拆为线性步骤，中间需 LLM gate |
| 2 | **Routing** | 路由 | 输入需分流到不同 handler |
| 3 | **Parallelization** | 并行化(Sectioning + Voting) | 独立子任务并行 / 多次投票 |
| 4 | **Orchestrator-Workers** | 主管-工人 | 主 LLM 动态拆任务派给 worker |
| 5 | **Evaluator-Optimizer** | 评估-优化循环 | 有清晰评估标准 + 迭代精炼有价值 |

### 关键原则

> *"The most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with **simple, composable patterns**."*

**中文**: 最成功的实现不是用复杂框架或专门库，而是用**简单可组合的模式**。
**潜台词**: 不要一上来就 LangGraph + LangSmith + 一堆中间件，先用最简单的模式跑通。

---

## 3. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "Don't use complex frameworks unless you need to." | 不需要时不用复杂框架。 | BEA 2024-12 |
| "Decompose a task into a sequence of steps... Add programmatic checks (a 'gate')." | 拆任务为步骤，中间加程序化校验闸门。 | BEA, Prompt Chaining |
| "LLMs can sometimes work simultaneously on a task, with their outputs aggregated programmatically." | LLM 有时可同时跑，结果由程序聚合。 | BEA, Parallelization |
| "Orchestrator-Workers are ideal for tasks with unpredictable complexity." | 主管-工人适合不可预测复杂度的任务。 | BEA, Orchestrator |
| "This workflow is particularly effective when we have clear evaluation criteria, and when iterative refinement provides measurable value." | 评估-优化循环最适合标准清晰 + 迭代有可衡量价值的任务。 | BEA, Evaluator-Optimizer |

---

## 4. 落地到本教程哪一章

| Pattern | 当前覆盖 | 状态 |
|---|---|---|
| Prompt Chaining | Ch6 `01_prompt_chaining.py` | ✅ 已实现 |
| Routing | Ch4.2.2 + Ch9 (L4) | ✅ 已实现 |
| Parallelization | Ch6 `02_parallelization.py` | ✅ 已实现 |
| Orchestrator-Workers | Ch4.2.4 SubAgent | ✅ 已实现 |
| Evaluator-Optimizer | Ch6 `03_evaluator_optimizer.py` + Ch7 (区分 Reflection) | ✅ 已实现 |

> **Anthropic 5 模式是当前教程做得最好的部分**——继续保持 Ch5/Ch6/Ch7 三章的纵深。

---

## 5. Sources

- [Building Effective AI Agents — Anthropic 官方页](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic news 版](https://www.anthropic.com/news/building-effective-agents)
- [Engineering 版（更技术）](https://www.anthropic.com/engineering/building-effective-agents)
- [Simon Willison summary (2024-12-20)](https://simonwillison.net/2024/Dec/20/building-effective-agents/)
- [Cloudflare Agents — anthropic-patterns README](https://github.com/cloudflare/agents/blob/main/guides/anthropic-patterns/README.md)

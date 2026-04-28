# Ch 6 · Five Workflow Patterns — Anthropic 五大流程模式

> **主线对应** (Mainline): Chase 5 级中的 **L2 (Single Call) → L3 (LLM Chain)**
>
> **大佬出处** (Reference): Anthropic *"Building Effective Agents"* (Schluntz & Zhang, 2024-12)
>
> **Anthropic 原文** (English):
> *"We've found that the most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns."*
>
> **中文翻译**：最成功的实现不是用复杂框架或专门库，而是用**简单可组合的模式**.

---

## 5 大模式对照表 (5 Patterns Glossary EN ↔ 中文)

| # | English | 中文 | 适用场景 | 本仓库实现位置 |
|---|---|---|---|---|
| 1 | **Prompt Chaining** | 提示词串联 | 任务可拆为线性步骤, 中间需 LLM gate | `01_prompt_chaining.py` (本章) |
| 2 | **Routing** | 路由 | 输入需分流到不同 handler | Ch4.2.2 (基础) + 本章 README 深化 |
| 3 | **Parallelization** | 并行化 (Sectioning + Voting) | 独立子任务并行 / 多次投票 | `02_parallelization.py` (本章) |
| 4 | **Orchestrator-Workers** | 主管-工人 | 主 LLM 动态拆任务派给 worker | Ch4.2.4 (基础) + 本章 README 深化 |
| 5 | **Evaluator-Optimizer** | 评估-优化循环 | 有清晰评估标准 + 迭代精炼有价值 | `03_evaluator_optimizer.py` (本章) |

---

## 双业务贯穿 (Dual Business Lines)

**主业务 (Primary)**: E-commerce Customer Service Bot **电商客服机器人**
**对照业务 (Comparison)**: Data Analyst Assistant **数据分析师助手**

每个 pattern 都用这两个业务做 demo, 让学员看见**同一模式跨业务通用**.

---

## 学完能力 (Learning Outcomes)

- 看到任务能立刻判断该用哪种 workflow pattern
- 会写 Prompt Chaining (含 LLM gate 中间校验)
- 会写 Parallelization (Sectioning 章节分割 + Voting 多数投票)
- 会写 Evaluator-Optimizer (生成 → 评估 → 改 → 直到达标)
- 知道**Routing 和 Orchestrator-Workers 何时用何时不用** (避免过度工程化)

## 脚本列表

| 脚本 | Pattern | 双业务案例 |
|---|---|---|
| `01_prompt_chaining.py` | **Prompt Chaining** | 客服: 投诉解析→分类→回复生成→敏感词 gate / 数分: 数据脱敏→统计→可视化 |
| `02_parallelization.py` | **Parallelization** | 客服: 5 LLM 投票判断意图 / 数分: 章节并行写报告 |
| `03_evaluator_optimizer.py` | **Evaluator-Optimizer** | 客服: 回复质量评估循环 / 数分: SQL 生成→执行→纠错循环 |
| `04_pattern_compare.py` | 5 模式对照实战 + 决策表 | 综合 |

## 一键验证

```bash
bash verify.sh
```

## Anthropic 原文金句 (Key Quotes)

> **On Prompt Chaining**: *"Decompose a task into a sequence of steps, where each LLM call processes the output of the previous one. Add programmatic checks (a 'gate') on intermediate steps."*
>
> 中文：把任务拆成一系列步骤，每个 LLM 调用处理上一个的输出。在中间步骤加程序化校验 ("gate").

> **On Parallelization**: *"LLMs can sometimes work simultaneously on a task, with their outputs aggregated programmatically. Two key variations: Sectioning (independent subtasks) and Voting (same task, multiple times for diverse outputs)."*
>
> 中文：LLM 有时可同时处理任务，结果由程序聚合. 两种变体: **章节分割** (独立子任务) 和 **投票** (同任务多次跑取多样输出).

> **On Evaluator-Optimizer**: *"This workflow is particularly effective when we have clear evaluation criteria, and when iterative refinement provides measurable value."*
>
> 中文：当评估标准清晰、迭代精炼有可衡量的价值时, 这个模式最有效.

## 下一步

学完 5 patterns → 进 [Ch 7 Reflection 模式](../ch07-reflection/) — Andrew Ng 4 patterns 之一, 主线 L4 路由 + 反思.

# Ch 7 · Reflection — 自我反思与改进 (核心漏点)

> **主线对应** (Mainline): Chase 5 级中的 **L4 (LLM Router) + Reflection on Generated Output**
>
> **大佬出处** (Reference): Andrew Ng *"Agentic Design Patterns"* — Pattern #1 of 4
>
> **Andrew Ng 原文** (English):
> *"Reflection alone, in some applications, gave bigger gains than upgrading the underlying model itself. The model automatically criticizes its own output and improves its response."*
>
> **中文翻译**：在某些应用中，**仅靠 Reflection 就能比升级底层模型本身带来更大的提升**. 模型自动批评自己的输出并改进.
>
> 详细参考 ref: [Andrew Ng — 4 Agentic Patterns](../../docs/references/big-names/05-andrew-ng.md) · 进阶类比 [Hassabis — DeepThink (AlphaGo-style search)](../../docs/references/big-names/03-hassabis.md) · Reflection 是 DeepThink 的单步版, ToT/搜索是它的深度版

---

## 学完能力 (Learning Outcomes)

- 理解 Reflection 与 Evaluator-Optimizer (Ch6/03) 的本质区别
- 会写**单 Agent 自评自改** (Self-Critique)
- 会写**双 Agent 生成-批评** (Generator-Critic)
- 会写**Tool-Grounded Reflection** (锚定工具结果反思 — 最强模式)
- 知道 **Reflection 的成本-收益权衡** (不是越多轮越好)

---

## Reflection vs Evaluator-Optimizer (核心区分)

| 维度 | Reflection (本章) | Evaluator-Optimizer (Ch6/03) |
|---|---|---|
| 角色 | **同一 LLM** 自反思 (single LLM self-critique) | **不同 system_prompt** 角色分离 (Generator vs Critic) |
| 心智模型 | "Agent 自我提升" (Andrew Ng) | "Workflow 流程编排" (Anthropic) |
| 实现 | Agent 内部多轮 | Chain 外部循环 |
| 成本 | 中 (单 LLM N 次) | 中-高 (Gen+Eval N 次) |
| 适用 | 创造性任务/写作/代码 | 有清晰评估标准的任务 |

> **关键区分** (Key Distinction): **Reflection 是 Agent 模式的自我提升, Evaluator-Optimizer 是 Workflow 模式的两角色协作**.

---

## 4 个脚本 (Scripts)

| 脚本 | 模式 | 中文 | 双业务案例 |
|---|---|---|---|
| `01_self_reflection.py` | **Self-Critique Loop** | 自我批评循环 | 客服: 回复初稿→自审→改 / 数分: 报告初稿→自审→改 |
| `02_two_agent_critique.py` | **Generator-Critic Pattern** | 生成-批评双 Agent | 客服: Gen Agent 写 + Critic Agent 挑刺 |
| `03_reflection_with_tools.py` | **Tool-Grounded Reflection** | 工具锚定反思 (最强) | 数分: LLM 写 Python → 跑 → 看 traceback → 改 |
| `04_multi_round_refinement.py` | **Iterative Refinement** | 多轮精炼 + 质量阈值 | 双业务: 设质量分 80 阈值, 不达标继续 |

## 一键验证

```bash
bash verify.sh
```

## Andrew Ng 原文金句 (Quotes)

> EN: *"I think reflection might be the most important and underrated agentic design pattern."*
>
> 中文：我认为 Reflection 可能是**最重要也是最被低估**的 Agent 设计模式.

> EN: *"By calling itself again with a critical prompt, the model can identify gaps and produce a much better response."*
>
> 中文：通过用一个批评性 prompt 再调用自己一次, 模型可以识别差距并产出**更好得多**的响应.

## 何时该用 / 不该用 (When to use / NOT use)

| ✅ 该用 | ❌ 不该用 |
|---|---|
| 创造性任务 (写作/设计/代码) | 严格延迟预算 (反思至少 2x latency) |
| 高质量要求 (法律/医疗文档) | 极简事实查询 (FAQ 退货政策) |
| 单次出错代价高 | 已知答案的封闭问题 |
| 有清晰可改进维度 (语气/正确性) | 没有"更好"标准的任务 |

## 下一步

学完 Reflection → 进 [Ch 8 工程化四件套](../ch08-engineering-pillars/) — OpenAI Practical Guide 的 Tools/Memory/Guardrails/Eval.

## 参考

- [Andrew Ng — 4 Agentic Design Patterns (Twitter)](https://x.com/AndrewYNg/status/1773393357022298617)
- [DeepLearning.AI — Agentic AI Course](https://learn.deeplearning.ai/courses/agentic-ai/)

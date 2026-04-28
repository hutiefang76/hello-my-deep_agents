# Ch 5 · Workflow vs Agent — 决策树 (Decision Tree)

> **Anthropic 核心命题** (*Building Effective Agents*, Schluntz & Zhang, 2024-12):
> "Workflows are systems where LLMs and tools are orchestrated through **predefined code paths**.
> In contrast, agents are systems where LLMs **dynamically direct their own processes** and tool usage."
>
> **中文翻译**：工作流是 LLM 和工具按**预定义代码路径**编排的系统；智能体是 LLM **自己动态决定流程**和工具使用的系统。

> **Harrison Chase 5 级自主性** (*Cognitive Architectures*, LangChain Blog):
> "There's a spectrum of autonomy in LLM applications: code → single LLM call → chain → router → autonomous agent."
>
> **中文翻译**：LLM 应用存在自主性谱系：硬编码 → 单次 LLM 调用 → 链 → 路由 → 自主智能体。
>
> 详细参考 ref: [Schluntz/Anthropic — Building Effective Agents](../../docs/references/big-names/04-anthropic-schluntz.md) · [Chase — Cognitive Architecture / 5 Levels](../../docs/references/big-names/06-chase.md)

---

## 学完能力 (Learning Outcomes)

- 拿到一个新需求, **能立刻判断该用 Workflow 还是 Agent** (Determinism vs Autonomy Tradeoff)
- 知道**5 级自主性阶梯**, 不会一上来就跳到 L5
- 理解为什么 Anthropic 反复强调 "Don't use complex frameworks unless you need to"

## 术语对照表 (Glossary EN ↔ 中文)

| English | 中文 | 出处 |
|---|---|---|
| Workflow | 工作流 (流程预定义) | Anthropic |
| Agent | 智能体 (LLM 自决) | Anthropic |
| Predefined Code Path | 预定义代码路径 | Anthropic |
| Determinism vs Autonomy Tradeoff | 确定性-自主性权衡 | Chase |
| Levels of Autonomy | 自主性等级 | Chase |
| Cognitive Architecture | 认知架构 | Chase |
| Agent Infrastructure | 智能体基础设施 | Chase |
| Hardcoded | 硬编码 (L1) | Chase |
| Single LLM Call | 单次 LLM 调用 (L2) | Chase |
| LLM Chain | LLM 链 (L3) | Chase |
| LLM Router | LLM 路由 (L4) | Chase |
| Autonomous Agent | 自主智能体 (L5) | Chase |

---

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_decision_tree.py` | 5 真实任务 → Workflow 还是 Agent? | `python src/01_decision_tree.py` |
| `02_five_autonomy_levels.py` | 同任务用 5 等级实现, 对比成本/可控性 | `python src/02_five_autonomy_levels.py` |
| `03_when_workflow_wins.py` | Workflow 比 Agent 好的 3 真实场景 | `python src/03_when_workflow_wins.py` |

## 一键验证

```bash
bash verify.sh
```

## 决策表 (Decision Matrix)

| 任务特征 | English | 推荐 |
|---|---|---|
| 步骤固定可枚举 | Steps are fixed and enumerable | **Workflow** |
| LLM 决定下一步 | LLM decides next step dynamically | **Agent** |
| 错一步代价高 (金融/医疗) | High cost of error | **Workflow** + Guardrails |
| 创造性任务 (写作/研究) | Creative / Open-ended | **Agent** |
| 严格成本预算 | Strict cost budget | **Workflow** (cheaper) |
| 强可观测性需求 | Strong observability requirement | **Workflow** (more transparent) |
| 用户能容忍多步 | User tolerates latency | **Agent** OK |
| 实时单步响应 | Real-time single-shot | **Workflow** |

## 大佬原文金句 (Quotes)

> **Anthropic**: "The most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns."
>
> 中文：最成功的实现不是用复杂框架或专门库，而是用**简单可组合的模式**。

> **Harrison Chase**: "Cognitive architecture is how you get your application to really work well — this is where teams are innovating."
>
> 中文：认知架构是让你的应用真正工作得好的关键——这是团队真正创新的地方。

## 下一步

学完 Ch5 → 进 [Ch 6 五大 Workflow Patterns](../ch06-workflow-patterns/) 把 Anthropic 5 模式逐个落地.

## 参考

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Harrison Chase — What is a Cognitive Architecture?](https://blog.langchain.com/what-is-a-cognitive-architecture/)
- [Chase — Own Architecture, Outsource Infrastructure](https://blog.langchain.com/why-you-should-outsource-your-agentic-infrastructure-but-own-your-cognitive-architecture/)

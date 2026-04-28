# Harrison Chase · LangChain CEO · Cognitive Architecture · 5 Levels of Autonomy

> LangChain / LangGraph / LangSmith 创始人 · **生态层 #1 影响者**
> 影响力: 他定义的"Cognitive Architecture"和"5 级自主性"是当前 Agent 设计的事实分类

---

## 1. 核心思想

### 1.1 5 Levels of Autonomy (自主性 5 级)

```
L1  ────────────────────────────────────────  L5
Hard-coded   Single LLM   LLM Chain   LLM Router   Autonomous Agent
   ⚙️           🧠           🔗           🚦              🤖
```

| Level | 名称 | 谁在做决定 | 何时该用 |
|---|---|---|---|
| L1 | Hardcoded | 你的代码 | 高确定性、低成本场景(FAQ) |
| L2 | Single LLM Call | LLM 一次决定 | 通用闲聊+简答 |
| L3 | LLM Chain | LLM 按你给的链 | 流程固定多步骤 |
| L4 | LLM Router | LLM 选下一步走哪条预定义分支 | 多意图分流 |
| L5 | Autonomous Agent | LLM 自己决定每一步 | 不可枚举的复杂任务 |

> *"There's a spectrum of autonomy in LLM applications: code → single LLM call → chain → router → autonomous agent."*

**中文**: LLM 应用存在自主性谱系——从纯硬编码到完全自主。

### 1.2 Cognitive Architecture（认知架构）

> *"Cognitive architecture is how you get your application to really work well — this is where teams are innovating."*

**中文**: 认知架构 = 让应用真正工作好的关键——这是团队真正创新的地方。

**定义**: 业务上的"决策树/工作流编排"，不是底层基础设施。
- 例 1: 客服机器人——什么问题走 L1 / 什么走 L5？这是认知架构
- 例 2: 退款流程——什么时候要人审核？这也是认知架构

### 1.3 Own Architecture, Outsource Infrastructure (2024)

> *"Own your cognitive architecture, outsource agent infrastructure. Cognitive architecture is your moat."*

**中文**:
- **拥有 (Own)**: 业务的认知架构 = 护城河
- **外包 (Outsource)**: Agent 基础设施(LangGraph/Checkpointer/Trace)

**为什么重要**: 这一刀切清楚——什么是企业核心资产(业务决策)，什么是 commodity(框架/中间件)。**框架可换，业务认知不可换**。

---

## 2. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "Cognitive architecture is your moat." | 认知架构是你的护城河。 | LangChain Blog 2024 |
| "Own your cognitive architecture, outsource your agent infrastructure." | 拥有认知架构，外包 Agent 基础设施。 | 同上 |
| "There's a spectrum of autonomy: code → single call → chain → router → agent." | 自主性是谱系，从硬编码到自主 Agent。 | What is Cognitive Architecture |

---

## 3. 落地到本教程哪一章

| 概念 | 当前覆盖 | 状态 |
|---|---|---|
| 5 Levels | Ch5 决策树 + Ch9 整章演化(L1-L5) | ✅ 优秀 |
| Cognitive Architecture | Ch9 README "Chase 论点深度解读" | ✅ 已点出 |
| Own/Outsource | Ch9 README 表格 (Own vs Outsource) | ✅ 已点出 |

> **本教程在 Chase 思想的覆盖上是行业领先水平**——Ch9 完整把 5 级演化用同一个真业务跑了一遍，比 Chase 自己的 blog 还落地。

**唯一改进**: Ch3 框架对比章应该明确说"我们用 LangGraph 是因为 Chase 路线，但 Cognitive Architecture 不绑定任何框架"——给学员留出"换框架不换思想"的灵活度。

---

## 4. Sources

- [What is a Cognitive Architecture? (LangChain Blog)](https://blog.langchain.com/what-is-a-cognitive-architecture/)
- [Own Architecture, Outsource Infrastructure](https://blog.langchain.com/why-you-should-outsource-your-agentic-infrastructure-but-own-your-cognitive-architecture/)
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [Harrison Chase X/Twitter](https://x.com/hwchase17)

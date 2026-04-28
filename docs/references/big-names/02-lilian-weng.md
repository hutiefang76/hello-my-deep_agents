# Lilian Weng · LLM Agent 三件套 · Lil'Log

> 前 OpenAI Safety/Applied AI 负责人 · Lil'Log 博客作者 · **整个 Agent 圈"事实标准"教科书的作者**
> 影响力: 她 2023-06 那篇 *LLM Powered Autonomous Agents* 是被引用次数最多的 Agent 综述，所有后续教程都在抄

---

## 1. 核心思想: Agent = LLM(Brain) + Plan + Memory + Tool Use

```
            ┌──────────────────────────┐
            │    LLM Agent (Brain)     │
            └─────┬──────┬──────┬──────┘
                  │      │      │
            ┌─────▼─┐ ┌──▼──┐ ┌─▼──────┐
            │ Plan  │ │ Mem │ │ Tools  │
            │       │ │     │ │        │
            │ subgo │ │ 短  │ │ web    │
            │ refl  │ │ 期  │ │ code   │
            │ ReAct │ │     │ │ db api │
            │ Tree  │ │ 长  │ │        │
            │ ofThou│ │ 期  │ │        │
            │       │ │ 向量│ │        │
            └───────┘ └─────┘ └────────┘
```

### 1.1 Planning（规划）

> *"The agent breaks down large tasks into smaller, manageable subgoals... can do self-criticism and self-reflection over past actions, learn from mistakes."*

**中文**: 把大任务拆成可管理的子目标；通过自我批评和反思，从错误中学习改进。

**子模式**: Subgoal decomposition / ReAct / Reflexion / Tree of Thoughts / Plan-and-Solve

### 1.2 Memory（记忆）

| 类型 | 类比人脑 | 实现 |
|---|---|---|
| Sensory Memory | 感觉记忆 | 原始输入(图/声) |
| Short-term Memory | 短期记忆 | In-context learning, 上下文窗口 |
| Long-term Memory | 长期记忆 | 向量库 + 快速检索 |

> *"Long-term memory provides the agent with the capability to retain and recall (infinite) information over extended periods, often by leveraging an external vector store."*

**中文**: 长期记忆让 Agent 能"无限"保留信息——靠外部向量库 + 快速检索实现。

### 1.3 Tool Use（工具使用）

> *"The agent learns to call external APIs for extra information that is missing from the model weights, including current information, code execution capability, access to proprietary information sources."*

**中文**: 训练后权重不再变了，但实时信息/代码执行/私有数据，Agent 通过调用外部 API 拿到。

---

## 2. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "Agent = LLM + memory + planning skills + tool use." | Agent = LLM + 记忆 + 规划 + 工具。 | X, 2023 |
| "This is probably just a start of a new era." | 这只是新纪元的开始。 | 同上 |
| "Memory in LLM agents is analogous to human memory: sensory, short-term (in-context), long-term (vector store)." | LLM 的记忆类比人脑：感觉/短期(上下文)/长期(向量库)。 | LLM Agents (2023-06) |

---

## 3. 落地到本教程哪一章

| 三件套 | 当前覆盖 | 改进动作 |
|---|---|---|
| Plan | Ch4.1 DeepAgents `write_todos` ✅ + Ch5 决策树 ✅ | 在 Ch3/总览加一张"Lilian Weng 三件套图"作为全书心智模型 |
| Memory | Ch4.2.1 三层 ✅ + Ch8 OpenAI 四层 ✅ | 在 Ch4.2.1 README 引用 Lilian Weng "类比人脑" 段落 |
| Tool Use | Ch2 ReAct ✅ + Ch4.2.3 ✅ + Ch8 ✅ | 同样补引用 |

**关键缺口**: 当前总览章 [docs/00-课程设计.md](../../00-课程设计.md) **没用三件套图作为全书纲领**——这是错过了一张"教科书级"的心智模型，必须补。

---

## 4. Sources

- [Lil'Log — LLM Powered Autonomous Agents (2023-06-23)](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Lilian Weng X tweet (一句话总纲)](https://x.com/lilianweng/status/1673535600690102273)
- [Lil'Log home (其他相关文章)](https://lilianweng.github.io/)
- [TuringPost summary on LinkedIn](https://www.linkedin.com/posts/theturingpost_we-decided-to-summarize-lilian-wengs-popular-activity-7122220214452133888-rUFa)

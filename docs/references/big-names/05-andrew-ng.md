# Andrew Ng · 4 Agentic Design Patterns · DeepLearning.AI

> 斯坦福教授 · Coursera 创始人 · DeepLearning.AI 创始人 · 中国学生最熟悉的"AI 入门祖师爷"
> 影响力: 他点名的"Reflection 是最被低估的 pattern"直接带火了 Reflection 模式

---

## 1. 核心思想: 4 Agentic Design Patterns (2024-03)

```
┌──────────────────────────────────────────────────┐
│         Andrew Ng's 4 Agentic Patterns           │
├──────────────────────────────────────────────────┤
│  ① Reflection         自我反思与改进              │
│  ② Tool Use           工具使用                    │
│  ③ Planning           规划                        │
│  ④ Multi-agent        多智能体协作                │
└──────────────────────────────────────────────────┘
```

### 1.1 Reflection（最重要也最被低估）

> *"Reflection alone, in some applications, gave bigger gains than upgrading the underlying model itself. The model automatically criticizes its own output and improves its response."*

**中文**: 在某些应用中，**仅靠 Reflection 就能比升级底层模型本身带来更大的提升**。模型自动批评自己的输出并改进。

> *"I think reflection might be the most important and underrated agentic design pattern."*

**中文**: 我认为 Reflection 可能是**最重要也是最被低估**的 Agent 设计模式。

**实现变体**:
1. Self-Critique — 同一 LLM 用批评性 prompt 调用自己
2. Generator-Critic — 两个独立 Agent 对抗
3. Tool-Grounded Reflection — 跑工具(代码/查询)看真结果，**最强**

### 1.2 Tool Use

调用搜索/计算/代码/数据库 → 用真实结果代替 LLM 幻觉。

### 1.3 Planning

把大任务拆成 N 步——和 Lilian Weng 的"Planning"重叠，但 Ng 强调"the bridge from short LLM chain to persistent agentic workflow"。

### 1.4 Multi-Agent Collaboration

> *"Multi-agent collaboration involves building multiple specialized agents — much like how a company might hire multiple employees — to perform a complex task."*

**中文**: 多智能体 = 像公司雇多个专业员工——研究员/批评家/写手/审稿人各司其职。

---

## 2. Andrew Ng 的教学哲学

> *"The course is taught in a vendor neutral way, using raw Python — without hiding details in a framework, showing how each step works."*

**中文**: 课程**用纯 Python 教学，不藏在框架里**，每一步都看得到。

**对我们的启示**: 当前教程过度依赖 DeepAgents/LangGraph 抽象——某些章节应该有"裸 Python 实现版"作为对照（让学员看清楚框架到底替你做了什么）。

---

## 3. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "Reflection alone gave bigger gains than model upgrade." | Reflection 单独就能比升级模型带来更大提升。 | X, 2024-03 |
| "Reflection is the most important and underrated pattern." | Reflection 是最重要也最被低估的模式。 | 同上 |
| "Multi-agent = hire multiple specialists for a complex task." | 多智能体 = 雇多个专家干一个复杂任务。 | 4 Patterns 系列 |
| "By calling itself again with a critical prompt, the model can identify gaps." | 用批评性 prompt 再调用自己一次，模型能识别差距。 | DeepLearning.AI 课 |

---

## 4. 落地到本教程哪一章

| 4 Patterns | 当前覆盖 | 状态 |
|---|---|---|
| Reflection | Ch7 (整章 4 脚本) | ✅ 优秀 |
| Tool Use | Ch2 / Ch4.2.3 / Ch8 | ✅ 已实现 |
| Planning | Ch4.1 (write_todos) + Ch5 | ✅ 已实现 |
| Multi-Agent | Ch4.2.4 SubAgent | ✅ 已实现 |

**额外动作**:
- 在 Ch7 README 顶部加一张"Andrew Ng 4 Patterns 全景图"——明确告诉学员"你正在学的是 4 之 1"
- 借鉴他的"vendor neutral / raw Python"教学法 → 在 Ch7 增加 `00_pure_python_reflection.py`（不调任何框架，纯 OpenAI/DashScope SDK）作为对照

---

## 5. Sources

- [Andrew Ng X — 4 Agentic Patterns (2024-03)](https://x.com/AndrewYNg/status/1773393357022298617)
- [DeepLearning.AI — Agentic AI Course (2025-10)](https://www.deeplearning.ai/courses/agentic-ai/)
- [Course Lesson Page (Agentic Design Patterns)](https://learn.deeplearning.ai/courses/agentic-ai/lesson/rm9bg7/agentic-design-patterns)
- [Andrew Ng LinkedIn post](https://www.linkedin.com/posts/andrewyng_one-agent-for-many-worlds-cross-species-activity-7179159130325078016-_oXr)
- [Hailey Quach — One Year After (Medium)](https://medium.com/@haileyq/agentic-ai-one-year-after-andrew-ngs-design-patterns-hype-or-reality-6fbd87dbe870)

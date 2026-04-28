# Demis Hassabis · DeepMind CEO · DeepThink / World Model / 2-Step AGI

> 国际象棋神童 + 神经科学博士 + DeepMind 联合创始人 · **AlphaGo 之父** · 2024 年诺贝尔化学奖得主（AlphaFold）
> 影响力: 学院派 AGI 路线的标杆 · 他的论点是"OpenAI 路线的对照组"

---

## 1. 核心思想

### 1.1 AGI 两步走 (Two Key Steps)

> *"To achieve AGI, two things must be accomplished: a world model that enables AI to truly understand physics and space, and automated experimentation which allows AI to solve fundamental problems through hands-on work."*

**中文**: 实现 AGI 必须做两件事:
1. **世界模型 (World Model)** — 让 AI 真正理解物理与空间
2. **自动化实验 (Automated Experimentation)** — 让 AI 通过"动手做"解决基础问题

**为什么重要**: 这是和 OpenAI "纯 scaling + RLHF" 路线最大的分歧——Hassabis 强调 *embodied + active learning*，不是单纯的语言模型 next-token 预测。

### 1.2 DeepThink (Gemini 2.5+, 2025-03)

> *"In Deep Think mode, Gemini is the most capable model that uses search and planning algorithms to explore lines of thought in parallel — an approach inspired by AlphaGo."*

**中文**: DeepThink 是 Gemini 最强模式，**用搜索+规划算法并行探索思路**——灵感来自 AlphaGo（蒙特卡洛树搜索）。

**对应到 Agent 设计**:
- **Reflection (Andrew Ng)** ≈ "对自己的输出做单步反省"
- **DeepThink (Hassabis)** ≈ "对未来 N 步的输出做多分支探索"
- 后者是前者的 *深度版* → 可以用 ToT (Tree of Thoughts) / ReWOO / Self-Refine 实现

### 1.3 Agent 是 DeepMind 的"出生设定" (since day 1)

> *"Building AI systems that can take action on their own has been DeepMind's focus since its early days."*

**中文**: 让 AI 能自主行动是 DeepMind 创立之初就在做的事——所以 DeepMind 的 Agent 路线天然带 RL+规划基因，区别于 NLP 出身的 OpenAI/Anthropic。

---

## 2. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "[Superintelligent] systems will need a world model and automated experimentation." | 超级智能系统需要世界模型 + 自动化实验。 | Hassabis 2025 访谈 |
| "DeepThink uses search and planning, inspired by AlphaGo." | DeepThink 用搜索 + 规划，灵感来自 AlphaGo。 | Gemini 2.5 发布 (2025-03) |
| "AGI requires reasoning, breaking down problems and carrying out actions in the world." | AGI 需要推理、分解问题、在现实中执行动作。 | Axios 访谈 (2024-12) |

---

## 3. 落地到本教程哪一章

| 思想 | 当前覆盖 | 改进动作 |
|---|---|---|
| Two-Step AGI (World Model + Auto-Experiment) | 全无 | docs/07-大佬思想全景.md 一段引用 + 解释为什么这暂超出本课范围 |
| DeepThink / Tree-of-Thought 风格搜索 | Ch7 Reflection 只覆盖"单步反思" | Ch7 加 `05_tree_of_thoughts.py` — 多分支探索 + best-path 选择，对应 Hassabis 的"AlphaGo-inspired"路线 |
| Agent 自主行动是天然路径 | Ch5 决策树有提"L5 自主 Agent" | Ch5 加金句 "DeepMind from day 1 builds for action, not chat" |

---

## 4. Sources

- [Axios — Hassabis on Gemini 2.0 agents (2024-12)](https://www.axios.com/2024/12/11/gemini-20-demis-hassabis-agents-ai)
- [Decoding DeepMind's Vision (substack)](https://aipositive.substack.com/p/decoding-deepminds-vision-an-analysis)
- [36kr — Two Key Steps to AGI](https://eu.36kr.com/en/p/3598888503902981)
- [Google Blog — Gemini 3 (2025-11)](https://blog.google/products-and-platforms/products/gemini/gemini-3/)
- [Hassabis on what's next (sources.news interview)](https://sources.news/p/interview-demis-hassabis-sources)

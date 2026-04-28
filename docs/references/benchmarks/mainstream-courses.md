# 主流 LLM/Agent 课程大纲对标 (2026)

> 用户追加要求 #1: "网搜参考别人怎么写"。本文汇总当前最具影响力的 LLM 应用课程大纲，作为本教程**目录设计的横向对照**。

---

## 1. mlabonne/llm-course (GitHub, 50K+ stars)

[GitHub: mlabonne/llm-course](https://github.com/mlabonne/llm-course)

```
LLM Fundamentals (基础)
├── 数学基础 (线性代数 / 微积分 / 概率)
├── Python for ML
├── Neural Networks
└── NLP

LLM Scientist (科学家路线)
├── Transformer architecture
├── Pre-training
├── Post-training (SFT / DPO / RLHF)
├── Evaluation
├── Quantization
└── New trends

LLM Engineer (工程师路线) ← 我们这本对标这条
├── Running LLMs (API / Local)
├── Vector storage
├── RAG (Retrieval Augmented Generation)
├── Advanced RAG (Hybrid / Reranking / HyDE)
├── Inference optimization
├── Deploying LLMs
├── Securing LLMs
└── Agent
```

**对标启示**:
- "Advanced RAG" 是单独章节——和我们 P0 的 Ch10 一致
- "Inference optimization / Deploying / Securing" 三章我们没覆盖

---

## 2. DeepLearning.AI · Agentic AI (Andrew Ng, 2025-10)

[DeepLearning.AI Course](https://learn.deeplearning.ai/courses/agentic-ai/information)

```
Module 1: Introduction to Agentic AI
Module 2: Reflection
Module 3: Tool Use
Module 4: Planning
Module 5: Multi-agent Collaboration
Module 6: Building Agents in Production
```

**对标启示**:
- 完全是 Andrew Ng 4 patterns 结构 — 我们 Ch7(Reflection) 借鉴了，但 Tool Use/Planning/Multi-agent 没作为单独章节明确点 4 patterns 标签
- 教学方式: **vendor neutral, raw Python, 不藏在框架里** — 我们过度依赖 DeepAgents 抽象

---

## 3. louisfb01/start-llms (GitHub)

[GitHub: louisfb01/start-llms](https://github.com/louisfb01/start-llms)

```
1. Foundations (Transformer / GPT / BERT)
2. Prompting & Prompt Engineering
3. Fine-tuning (LoRA / QLoRA / PEFT)
4. RAG (含 Advanced RAG)
5. Agents (ReAct / Plan-and-Execute)
6. Evaluation
7. Deployment (vLLM / Ollama / Triton)
8. Security
```

**对标启示**:
- 把 Fine-tuning 放在 RAG 之前——很多教程其实倾向"先 RAG 后 Fine-tuning"，因为 RAG 性价比远高于 Fine-tuning
- 我们不深入 Fine-tuning 是合理选择(目标是"应用工程师")

---

## 4. AI Engineer Roadmap (Devin Rosario, 2026 DEV)

[DEV — LLM Mastery 2026 Roadmap](https://dev.to/devin-rosario/llm-mastery-skip-the-math-focus-on-rag-2026-roadmap-5fb)

**核心论点**: "**Skip the Math, Focus on RAG**" — 应用工程师不需要懂梯度下降，需要懂 RAG。

```
Phase 1: API & Prompt Engineering (0→1)
Phase 2: RAG (核心阶段)
Phase 3: Agents (LangGraph / LlamaIndex Agents)
Phase 4: Evaluation & Observability (LangSmith / Phoenix)
Phase 5: Production (vLLM / Ollama / FastAPI)
```

---

## 5. AI Engineer Core Track (Udemy)

[LLM Engineering Master Course](https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models/)

```
- Frontier models (GPT-4 / Claude / Gemini)
- Open source models (Llama / Qwen / DeepSeek)
- Model selection 决策表
- RAG (基础 + 进阶)
- Fine-tuning (LoRA / QLoRA)
- Agentic workflows
```

---

## 6. 业界共识 — 必覆盖主题清单

我做了横向对照，从上述 5 套课程提取出**至少 4 家覆盖**的主题:

| 主题 | mlabonne | DLAI | start-llms | DEV | Udemy | **本教程** |
|---|---|---|---|---|---|---|
| Prompt Engineering | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ Ch2 较浅 |
| **Context Engineering** | ⚠️ | — | — | — | — | ❌ 全无 |
| Vector Storage | ✅ | — | ✅ | ✅ | ✅ | ⚠️ 只 InMemory |
| Basic RAG | ✅ | — | ✅ | ✅ | ✅ | ✅ Ch4.2.3 |
| **Advanced RAG (Hybrid/Rerank)** | ✅ | — | ✅ | ✅ | ✅ | ❌ **0 实现** |
| Tool Use / Function Calling | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ReAct / Plan-Solve | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ 只 ReAct |
| **Reflection** | — | ✅ | — | — | — | ✅ Ch7 |
| Multi-agent | ✅ | ✅ | ✅ | ✅ | — | ✅ Ch4.2.4 |
| **Memory (多层)** | — | — | — | — | — | ✅ **我们最强** |
| Workflow Patterns | — | — | — | — | — | ✅ **我们独有** |
| Cognitive Architecture | — | — | — | — | — | ✅ **我们独有** |
| Evaluation | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ Ch8 浅 |
| Observability (Trace) | ✅ | ✅ | — | ✅ | ✅ | ⚠️ 提了未跑 |
| **Deployment** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Security/Guardrails** | ✅ | — | ✅ | — | — | ⚠️ Ch8 浅 |
| **MCP/A2A 协议** | — | — | — | — | — | ❌ |
| Fine-tuning | ✅ | — | ✅ | — | ✅ | ❌(故意不做) |

**红色缺口** (4 家以上覆盖但我们 0):
- Advanced RAG (P0 必补 → Ch10)
- Deployment

**蓝色独有优势** (其他教程没有但我们有):
- 多层记忆系统化 (Lilian Weng + OpenAI 4 层)
- Workflow Patterns (Anthropic 5 模式)
- Cognitive Architecture L1-L5 演化

---

## 7. 总结: 我们的差异化定位

```
其他教程: "什么都教一点" — 广度优先
本教程:   "用 Java 工程师视角 + 深度 Patterns + Cognitive Architecture"
          — 深度优先 + 类比驱动

差异化优势:
✅ Spring Boot 类比 (其他教程都没有)
✅ 5 Workflow Patterns 独立章节 (其他没有)
✅ L1→L5 演化对比 (其他没有)
✅ 多层记忆系统化梳理 (其他散落)

必须补齐的"卫生底线":
❌ Advanced RAG (Ch10)
❌ Context Engineering (Ch11)
❌ MCP 协议 (Ch12, 来自 llm_study)
❌ 评估实操 (Ch8 升级)
```

---

## Sources

- [mlabonne/llm-course](https://github.com/mlabonne/llm-course)
- [louisfb01/start-llms](https://github.com/louisfb01/start-llms)
- [DeepLearning.AI Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/)
- [DEV LLM Mastery 2026 Roadmap](https://dev.to/devin-rosario/llm-mastery-skip-the-math-focus-on-rag-2026-roadmap-5fb)
- [Udemy AI Engineer Core Track](https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models/)
- [DataCamp LLMs Concepts](https://www.datacamp.com/courses/large-language-models-llms-concepts)
- [MachineLearningMastery — Reading List 2026](https://machinelearningmastery.com/a-beginners-reading-list-for-large-language-models-for-2026/)
- [SecondTalent — Top 7 LLM Books 2026](https://www.secondtalent.com/resources/top-books-on-llms-for-beginners-to-advanced/)
- [Coursera LLM Courses](https://www.coursera.org/courses?query=large+language+models)

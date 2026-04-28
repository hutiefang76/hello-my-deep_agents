# Andrej Karpathy · LLM OS · Software 2.0 · Context Engineering

> 江湖称号: **k 神** · 前 OpenAI 创始团队 + 前 Tesla AI 总监 · "Intro to LLMs" 教程作者
> 影响力: Twitter/X 上 LLM 圈 #1 思想领袖，**他说什么半年内就是行业共识**

---

## 1. 核心思想 (Three Big Ideas)

### 1.1 Software 2.0 (2017, 仍是底层世界观)

> *"Software 2.0 is written in much more abstract, human unfriendly language, such as the weights of a neural network."*

**中文**: Software 2.0 是用神经网络权重写的代码——你写训练数据 + loss，编译器(SGD)生成权重；区别于人类敲键盘写的 Software 1.0。

**为什么重要**: 这是看待 LLM 的根基视角——Prompt 不是"输入"，是 *Software 2.0 时代的"代码片段"*。

### 1.2 LLM OS (2023-11, "Intro to LLMs" 演讲)

```
                ┌─────────────────────────────────┐
                │          LLM (kernel)           │
                │   ┌──────────────────────┐      │
                │   │  weights · context   │      │
                │   └──────────────────────┘      │
                └────┬────────┬──────┬────────────┘
                     │        │      │
              ┌──────▼─┐  ┌───▼──┐  ▼
              │ Memory │  │Tools │ I/O (Vision/Audio/Text)
              │ (RAG/  │  │(Web/ │
              │ Vector)│  │ Code)│
              └────────┘  └──────┘
```

> *"LLM should not be thought of as a chatbot or work generator. Instead, LLMs should be thought of as the kernel process of an emerging operating system."*

**中文**: LLM 不应被当成聊天机器人，应被当成新型操作系统的内核——上下文窗口=RAM，向量库=磁盘，工具=系统调用，多模态=I/O。

**对应到 DeepAgents**: DeepAgents 的 4 件套（write_todos / virtual FS / SubAgent / system_prompt）正是 LLM OS 模型的具象化——`virtual FS` ≈ 磁盘，`SubAgent` ≈ 进程，`write_todos` ≈ 任务调度器。

### 1.3 Context Engineering (2025, 与 Tobi Lütke 联袂背书)

> *"+1 for 'context engineering' over 'prompt engineering'. People associate prompts with short task descriptions you'd give an LLM in your day-to-day use. When in every industrial-strength LLM app, **context engineering is the delicate art and science of filling the context window with just the right information for the next step**."*
> — Karpathy, X (twitter), 2025-06

**中文**: 我支持用「上下文工程」替代「提示词工程」。提示词被人理解成日常聊天的简短指令，但**任何工业级 LLM 应用，真正考验的是上下文工程**——精心设计：往这次推理的上下文窗口里塞什么、不塞什么、怎么排序。

**为什么重要**:
- Prompt Engineering = 微观技巧（魔法咒语）
- Context Engineering = 宏观系统（架构决策）
- 这是 2022-2024 → 2025 → 2026+ 的能力演进路径

---

## 2. 原文金句 (English ↔ 中文)

| EN | 中文 | 出处 |
|---|---|---|
| "LLM = zip file of the internet, ~100x compression." | LLM = 互联网的 zip 包，约 100 倍压缩。 | Intro to LLMs (2023) |
| "An LLM is basically two files: parameters and a ~500-line C runner." | 一个 LLM 本质就是两个文件：权重 + 约 500 行 C 代码的 runner。 | 同上 |
| "Context engineering is the delicate art of filling the context window with just the right information." | 上下文工程是往窗口里精心填入"恰到好处的信息"的艺术。 | X, 2025-06 |
| "We're moving from Prompt Engineering → Context Engineering → Harness Engineering." | 演进路径：提示词工程 → 上下文工程 → 工装工程(给自主 agent 设计运行环境)。 | (社区共识，2026 起) |

---

## 3. 落地到本教程哪一章

| 卡片观点 | 当前缺口 | 应落到哪 |
|---|---|---|
| LLM OS | Ch4.1 DeepAgents 介绍只讲了"4 件套"，没拉到 OS 视角 | Ch4.1 README 加图 + Ch11 Context Engineering 开篇 |
| Software 2.0 | 全教程没出现 | docs/00-课程设计.md 开篇加一节"为什么这是新工种" |
| Context Engineering | **完全缺失**（仅 Anthropic 的"system prompt"提了一嘴） | **新增 Ch11** · 含 `01_karpathy_llm_os.py` 把记忆/工具/FS 重新组织成 LLM OS 抽象 |

---

## 4. Sources

- [Intro to LLMs (YouTube/原视频)](https://www.youtube.com/watch?v=zjkBMFhNj_g)
- [Illustrated LLM OS (HuggingFace blog)](https://huggingface.co/blog/shivance/illustrated-llm-os)
- [Karpathy on Context Engineering (X)](https://x.com/karpathy/status/1937902205765607626)
- [Software 2.0 (medium, 2017)](https://karpathy.medium.com/software-2-0-a64152b37c35)
- [The Technical User's Intro to LLMs (christophergs)](https://christophergs.com/blog/intro-to-large-language-models-llms)

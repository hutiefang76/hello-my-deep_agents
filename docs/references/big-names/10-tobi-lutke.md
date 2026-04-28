# Tobi Lütke · Shopify CEO · Context Engineering Endorsement

> Shopify CEO · 工程师 CEO 代表 · **2025 与 Karpathy 联袂带火"Context Engineering"概念**
> 影响力: 他不是 LLM 学者，但作为大厂 CEO 在生产环境用 LLM 的发言比学者更接地气

---

## 1. 核心论断: Context Engineering 定义

> *"Context engineering is the art of providing all the context for the task to be plausibly solvable by the LLM."*
> — Tobi Lütke, X, 2025

**中文**: 上下文工程 = **提供让任务对 LLM 可解的全部上下文**的艺术。

### 关键词拆解

| 词 | 含义 |
|---|---|
| **All the context** | 不只 prompt——还包括: 历史对话/检索结果/工具描述/Few-shot 例子/用户画像/系统状态 |
| **Plausibly solvable** | LLM 是概率系统——你的任务是把任务从"不可能"变成"概率可解"，不是"必然正确" |
| **Art** | 没有银弹——需要工程判断 + 持续调优 |

---

## 2. 与 Karpathy 联袂效应

```
Tobi Lütke (CEO 视角)        +        Karpathy (技术视角)
"Provide all context"                  "Fill the context window
                                        with just the right info"
            ↓                                       ↓
       2025 中期社区共识：Context Engineering 替代 Prompt Engineering
```

> Simon Willison 评论: *"Prompt engineering had been redefined to mean typing prompts full of stupid hacks into a chatbot."*

**中文**: "提示词工程"这个词被用滥了——变成"往聊天框里输入一堆奇葩咒语"。需要新词标识真正的工程实践。

---

## 3. 三阶段演进 (社区共识)

```
2022-2024: Prompt Engineering        消息级指令设计
   ↓
2025:      Context Engineering       架构化"模型推理时看到什么"
   ↓
2026+:     Harness Engineering       为自主 Agent 设计完整运行环境
```

---

## 4. 落地到本教程哪一章

| 概念 | 当前覆盖 | 改进动作 |
|---|---|---|
| Context Engineering 定义 | ❌ 全无 | **新增 Ch11 · Context Engineering 整章**(已在 P0 闭环清单) |
| 三阶段演进 | ❌ 全无 | docs/07-大佬思想全景.md 加图 |
| 生产 CEO 视角 | ❌ 全无 | Ch11 引用 Tobi 的话——"作为大厂 CEO，我看的是任务能不能完成，不是 prompt 多漂亮" |

**Ch11 拟设计**:

```
labs/ch11-context-engineering/
├── 01_prompt_vs_context.py        Prompt Engineering vs Context Engineering 对比
├── 02_karpathy_llm_os.py          LLM OS 视角组织上下文
├── 03_brockman_4part.py            Goal/Format/Warning/Context Dump 框架
├── 04_context_window_budget.py     Token 预算分配 (system/history/RAG/tools)
└── 05_harness_engineering.py       为自主 Agent 设计完整 harness 的预览
```

---

## 5. Sources

- [Karpathy on Context Engineering (X 2025-06)](https://x.com/karpathy/status/1937902205765607626)
- [Phil Schmid — Context Engineering](https://www.philschmid.de/context-engineering)
- [Simon Willison — Context Engineering note](https://simonwillison.net/2025/Jun/27/context-engineering/)
- [Prompting Guide — Context Engineering](https://www.promptingguide.ai/guides/context-engineering-guide)
- [Atlan — Prompt vs Context vs Harness](https://atlan.com/know/harness-engineering-vs-prompt-engineering/)
- [Aakashg — Ultimate Guide for PMs](https://www.news.aakashg.com/p/context-engineering)
- [Zep blog — What is Context Engineering](https://blog.getzep.com/what-is-context-engineering/)

# Context Engineering · 上下文工程 · 2025 行业转向

> **核心定位**: 这是 2025 年 LLM 圈最大共识转向——Karpathy + Tobi Lütke 联袂背书，整个工程实践从"Prompt Engineering"升级到"Context Engineering"。
> 用户原始目标 #4 要求融入"k 神"等大佬观点——本主题是 Karpathy 思想的核心载体。

---

## 1. 三阶段演进

```
┌──────────────────────┬───────────────────┬────────────────────┐
│  Prompt Engineering  │ Context Engineering│ Harness Engineering│
│      (2022-2024)     │      (2025)       │     (2026+)        │
├──────────────────────┼───────────────────┼────────────────────┤
│ 单条消息怎么写        │ 整个上下文怎么组装 │ 自主 Agent 整套环境 │
│ "Step by step"咒语    │ system + RAG +    │ 工具集+权限+预算    │
│ Few-shot example     │ history + tool    │ 监控+回滚+审批       │
│ JSON 结构提示        │ desc + user state │ 长期 memory 管理     │
└──────────────────────┴───────────────────┴────────────────────┘
```

---

## 2. 权威定义

### Karpathy (2025-06)
> *"Context engineering is the delicate art and science of filling the context window with just the right information for the next step."*

**中文**: 上下文工程是**为下一步推理把上下文窗口填入"恰到好处的信息"**——这是精细的艺术和科学。

### Tobi Lütke (2025)
> *"Context engineering is the art of providing all the context for the task to be plausibly solvable by the LLM."*

**中文**: 上下文工程 = **提供让任务对 LLM 可解的全部上下文**的艺术。

### Phil Schmid (HuggingFace 工程师, 2025)
> *"The new skill in AI is not prompting, it's context engineering."*

**中文**: AI 时代的新技能不是 prompt，是 context engineering。

---

## 3. Context 包含什么 (清单)

```
Context Window 内容清单
─────────────────────
1. System Prompt          身份/角色/约束
2. Tool Descriptions       工具签名 + 用法
3. Few-shot Examples       范例(可静态可动态)
4. User Profile / State   用户画像/会话状态/权限
5. RAG Retrieval Chunks   检索来的相关文档(top-K)
6. Conversation History   多轮对话历史(可摘要)
7. Tool Results            工具调用的返回值
8. Scratchpad / Plan      Agent 自己的中间思考
9. Output Format Schema    返回格式定义
10. Warnings / Red Lines   红线 + 必查项
```

**工程问题**:
- Token 预算怎么分配 (system 占 X%, RAG 占 Y%, history 占 Z%)？
- 哪些是"每次都贴"，哪些是"按需检索"？
- 多轮对话超长时怎么压缩(摘要/淘汰/分层)？
- Tool Description 太多怎么动态过滤？

---

## 4. 5 大常见反模式 (Anti-Patterns)

| 反模式 | 后果 | 对应正解 |
|---|---|---|
| 把所有 RAG 结果一股脑贴 | Context Pollution | top-K 限制 + Reranker |
| Tool Description 不管多少全塞 | 工具选错率高 | 按场景动态过滤 |
| 历史消息不压缩 | Token 爆 + 关键信息被淹 | Summary memory + 滑窗 |
| 用户 profile 始终全量贴 | 浪费 + 隐私风险 | 按当前任务相关性裁剪 |
| 没有 output schema | 结构不稳定 | 强制 JSON / Pydantic schema |

---

## 5. 落到本教程: 新增 Ch11 设计

```
labs/ch11-context-engineering/
├── README.md (引用 Karpathy + Tobi 原话)
├── src/
│   ├── 01_prompt_vs_context.py      
│   │     # 同一任务, 业余 prompt vs 完整 context — 看输出稳定性差异
│   ├── 02_karpathy_llm_os.py
│   │     # 把 messages/RAG/tools/files 重新组织成 LLM OS 抽象
│   ├── 03_brockman_4part.py
│   │     # Goal/Format/Warning/Context Dump 4 段式实战
│   ├── 04_token_budget.py
│   │     # 8K context 如何分配: system/history/RAG/tools 4 类预算
│   ├── 05_dynamic_tool_filter.py
│   │     # 根据意图动态过滤可用工具 — 减小 context 噪声
│   └── 06_history_compression.py
│         # 滑窗 / 摘要 / 分层 三种历史压缩对比
└── verify.sh
```

---

## 6. Sources (全部真实可点击)

- [Andrej Karpathy on Context Engineering (X 2025-06-25)](https://x.com/karpathy/status/1937902205765607626)
- [Phil Schmid — The New Skill is Context Engineering](https://www.philschmid.de/context-engineering)
- [Simon Willison — Context Engineering (2025-06-27)](https://simonwillison.net/2025/Jun/27/context-engineering/)
- [Prompting Guide — Context Engineering Guide](https://www.promptingguide.ai/guides/context-engineering-guide)
- [Atlan — Prompt vs Context vs Harness](https://atlan.com/know/harness-engineering-vs-prompt-engineering/)
- [Addy Osmani — Context Engineering: Bringing Engineering Discipline](https://addyo.substack.com/p/context-engineering-bringing-engineering)
- [Aakash Gupta — Ultimate Guide for PMs](https://www.news.aakashg.com/p/context-engineering)
- [Zep — What is Context Engineering](https://blog.getzep.com/what-is-context-engineering/)
- [36kr — Context Engineering 在硅谷火了](https://eu.36kr.com/en/p/3366869315372801)
- [University of Idaho AI4RA — From Prompt to Context Engineering](https://ai4ra.uidaho.edu/from-prompt-engineering-to-context-engineering/)

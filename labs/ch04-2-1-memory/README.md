# Ch 4.2.1 · 多层记忆

> Agent 的"记忆"分三层 — 短期 / 会话 / 长期, 各自解决不同问题.
>
> 心智模型 ref: [Lilian Weng — Agent = Plan + Mem + Tool](../../docs/references/big-names/02-lilian-weng.md) · 三层记忆类比人脑感觉/短期/长期, 是整本教程的全书心智模型.

## 三层记忆对照

| 层 | 范围 | 存储位置 | 解决什么问题 | 本 lab 用什么 |
|---|---|---|---|---|
| **短期** | 同一次 invoke 内 | messages 列表 | LLM 看到对话上下文 | Python 列表 + 窗口截断 |
| **会话** | 同一个 thread 跨多次 invoke | Checkpointer | 用户关掉再回来还能续上 | LangGraph SqliteSaver |
| **长期** | 跨所有会话 / 跨用户 | 向量库 | "你上次说过 X" 这种远期回忆 | InMemoryVectorStore + DashScope embeddings |

## 学完能力

- 知道何时该用短期 / 会话 / 长期记忆
- 会用 LangGraph 的 Checkpointer 让 Agent 跨次对话保持上下文
- 会用向量检索让 Agent 拥有"远期回忆"
- 能把三层记忆组合到一个 Agent 上

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_short_term.py` | messages 列表 + 窗口截断 | `python src/01_short_term.py` |
| `02_session_checkpointer.py` | LangGraph SqliteSaver, 跨 turn 续会话 | `python src/02_session_checkpointer.py` |
| `03_long_term_vector.py` | 向量库存历史对话 + 语义检索 | `python src/03_long_term_vector.py` |
| `04_three_layers_combined.py` | 三层组合实战 | `python src/04_three_layers_combined.py` |

## 一键验证

```bash
bash verify.sh
```

注: 04 脚本需要 1-2 分钟（多次 LLM 调用 + embedding 调用）.

## 关键代码片段速查

### 短期 — messages 窗口
```python
WINDOW = 10
recent = messages[-WINDOW:]    # 只保留最近 10 条
```

### 会话 — Checkpointer
```python
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("memory.db")
agent = create_deep_agent(model, tools, system_prompt=..., checkpointer=checkpointer)
agent.invoke(input, config={"configurable": {"thread_id": "alice-2026-04-27"}})
```

### 长期 — 向量检索
```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings

vs = InMemoryVectorStore(DashScopeEmbeddings(model="text-embedding-v3"))
vs.add_texts(["昨天用户喜欢 LangChain", "前天用户提到喜欢 Python"])
relevant = vs.similarity_search("用户关心什么技术", k=2)
```

## 下一步

学完记忆 → 进 [Ch 4.2.2 意图识别 + 路由](../ch04-2-2-intent/) 教 Agent 区分用户意图.

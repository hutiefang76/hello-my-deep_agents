# Ch 4.2.2 · 意图识别 + 路由

> 让 Agent 区分用户在问什么 (FAQ / 订单 / 退款 / 闲聊), 然后走不同的处理分支.

## 学完能力

- 用 Pydantic Schema + `with_structured_output` 做意图分类
- 用 LangGraph StateGraph 写条件路由 (类似 Spring StateMachine)
- 在 DeepAgent 中嵌入意图识别 (前置分流)

## 应用场景

- 智能客服: 分流 FAQ / 售后 / 投诉 / 闲聊
- IDE 助手: 分流 写代码 / 解释 / 重构 / 调试
- 数据助手: 分流 查询 / 分析 / 可视化

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_intent_classify.py` | Pydantic Schema 结构化意图分类 | `python src/01_intent_classify.py` |
| `02_state_graph_routing.py` | LangGraph StateGraph 条件路由 | `python src/02_state_graph_routing.py` |
| `03_intent_with_deepagent.py` | DeepAgent + 意图识别前置分流 | `python src/03_intent_with_deepagent.py` |

## 一键验证

```bash
bash verify.sh
```

## 关键代码片段

### 意图分类 — Pydantic Schema
```python
class Intent(BaseModel):
    category: Literal["faq", "order", "refund", "chitchat"]
    confidence: float
    extracted_entities: dict

structured_llm = llm.with_structured_output(Intent)
intent = structured_llm.invoke("我想退货")
# intent.category == "refund"
```

### LangGraph 条件路由
```python
def route(state) -> str:
    return state["intent"]  # 由 classify 节点写入

workflow.add_conditional_edges("classify", route, {
    "faq":      "handle_faq",
    "order":    "handle_order",
    "refund":   "handle_refund",
    "chitchat": "handle_chitchat",
})
```

### DeepAgent 前置分流
```python
# 把意图识别结果塞进 system_prompt, 让 DeepAgent 走对应路径
intent = classify(user_msg)
agent.invoke({"messages": [
    SystemMessage(content=f"用户意图={intent.category}, 走 {intent.category} 处理流程"),
    HumanMessage(content=user_msg),
]})
```

## 下一步

学完意图 → 进 [Ch 4.2.3 工具调用 + RAG](../ch04-2-3-tools-rag/) 让 Agent 具备业务能力.

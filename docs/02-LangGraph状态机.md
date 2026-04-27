# LangGraph 状态机 — 5 分钟入门

> Spring StateMachine 的 LLM 版.

## 1. 核心抽象

LangGraph 把 Agent 看成"状态机":
- **状态 (State)**: TypedDict, 含 messages / 业务字段
- **节点 (Node)**: Python 函数, 接 state 返回 state 增量
- **边 (Edge)**: 节点之间的跳转规则
- **图 (StateGraph)**: 节点 + 边的集合, compile() 后变成 Runnable

## 2. 最简示例

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

# 1. 定义状态
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]   # add_messages 是 reducer

# 2. 定义节点
def llm_node(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}    # 返回增量, 由 add_messages 合并

def tool_node(state: State) -> dict:
    last = state["messages"][-1]
    results = [execute_tool(tc) for tc in last.tool_calls]
    return {"messages": results}

# 3. 构图
workflow = StateGraph(State)
workflow.add_node("llm", llm_node)
workflow.add_node("tool", tool_node)
workflow.add_edge(START, "llm")

# 4. 条件边: llm 决定下一步
def should_continue(state: State) -> str:
    last = state["messages"][-1]
    return "tool" if last.tool_calls else END

workflow.add_conditional_edges("llm", should_continue, {"tool": "tool", END: END})
workflow.add_edge("tool", "llm")    # tool 跑完回 llm 节点

# 5. 编译 + 调用
graph = workflow.compile()
result = graph.invoke({"messages": [HumanMessage(content="天气怎么样?")]})
```

## 3. 关键能力

### 3.1 add_messages reducer

`add_messages` 是 LangGraph 提供的 reducer, 自动:
- 合并 messages 列表 (不是覆盖)
- 处理 ID 去重
- 兼容多种消息格式

类比 Redux 的 reducer, 但内置好了.

### 3.2 Checkpointer 持久化

```python
from langgraph.checkpoint.sqlite import SqliteSaver

graph = workflow.compile(checkpointer=SqliteSaver.from_conn_string("memory.db"))

# 第一次 invoke
graph.invoke(input, config={"configurable": {"thread_id": "user-001"}})

# 重启程序后, 同 thread_id 可以续上 (state 自动加载)
graph.invoke(new_input, config={"configurable": {"thread_id": "user-001"}})
```

类比 Spring StateMachine 的 `StateMachinePersister`.

### 3.3 stream_mode

```python
# 流式: 看每个节点的输出
for step in graph.stream(input, stream_mode="updates"):
    for node_name, output in step.items():
        print(f"[{node_name}] {output}")

# 流式 token 级
for chunk in graph.stream(input, stream_mode="messages"):
    print(chunk[0].content, end="", flush=True)
```

### 3.4 prebuilt.create_react_agent

LangGraph 内置一行启动 ReAct Agent:

```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)
```

但它**不是** DeepAgents — 没有 Planning Tool / FS / SubAgent.

## 4. 何时用 LangGraph 直接

- 状态有复杂业务字段 (不只是 messages)
- 需要显式条件分支 (5+ 个 handler)
- 需要断点续跑 / 人工干预 (interrupt)
- 需要可视化工作流图 (graph.get_graph().draw_mermaid())

否则用 DeepAgents 就够了.

## 5. 与 DeepAgents 的关系

```
DeepAgents
   ↓ 内部基于
LangGraph
   ↓ 内部基于
LangChain Core (Runnable / Messages)
```

DeepAgents 把 LangGraph 的 StateGraph + 内置工具封装成一行 `create_deep_agent`.

## 6. 参考

- LangGraph docs: https://langchain-ai.github.io/langgraph/
- 本仓库实践: 见 [labs/ch03-frameworks-compare/src/02_langgraph.py](../labs/ch03-frameworks-compare/src/02_langgraph.py)
- 状态机路由: 见 [labs/ch04-2-2-intent/src/02_state_graph_routing.py](../labs/ch04-2-2-intent/src/02_state_graph_routing.py)

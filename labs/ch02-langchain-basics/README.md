# Ch 2 · LangChain 基础

> 5 个脚本带你掌握 LangChain 0.3 的核心 API.

## 学完能力

- 会用 ChatTongyi / ChatOpenAI 调通义千问
- 会写 Prompt 模板和 Few-shot
- 会用 LCEL 表达式 `prompt | llm | parser` 拼链
- 会用 `@tool` 装饰器写自定义工具, 让 LLM 调
- 会用 LangGraph 的 `create_react_agent` 跑 ReAct Agent

## 前置依赖

- 完成 Ch1
- `.env` 里 `DASHSCOPE_API_KEY` 已配置 (能跑 `python scripts/check-env.py`)
- `pip install -r requirements.txt` 已装好

## 脚本列表

| 脚本 | 主题 | 核心 API |
|---|---|---|
| `01_chat_basic.py` | LLM 调用 + 流式 + 异步 | `ChatTongyi.invoke()` / `stream()` / `ainvoke()` |
| `02_prompt_template.py` | Prompt 模板 + Few-shot | `ChatPromptTemplate.from_messages` |
| `03_lcel_chain.py` | LCEL 链式表达式 | `prompt | llm | parser` |
| `04_tool_call.py` | 工具调用 (function calling) | `@tool` + `llm.bind_tools()` |
| `05_react_agent.py` | ReAct Agent (LangGraph 官方) | `create_react_agent` |

## 一键验证

```bash
bash verify.sh
```

每个脚本都会**真实调用 DashScope API**, 单个脚本约 1-3 秒, 全部跑完约 30 秒.

## 关键概念

### LCEL — LangChain Expression Language

```python
chain = prompt | llm | parser
result = chain.invoke({"topic": "AI"})
```

类比 Java 8 Stream: `stream.map(...).filter(...).collect(...)`, LCEL 是 LLM 版的"管道操作".

### 工具调用 (Function Calling)

LLM 不再"假装"调函数, 而是返回结构化的 `tool_calls`, 由你的代码真实执行后回传给 LLM.

```python
@tool
def get_weather(city: str) -> str:
    """查询某城市的天气."""
    return f"{city}: 26°C, 晴"

llm_with_tools = llm.bind_tools([get_weather])
```

### ReAct Agent

Reasoning + Acting 循环: LLM 推理 → 调工具 → 看结果 → 再推理 → ... → 给答案.

LangGraph 官方一行实现: `agent = create_react_agent(llm, tools, prompt)`.

## 下一步

学完 Ch2 → 进 [Ch 3 框架对比](../ch03-frameworks-compare/) 看同样任务用三种框架怎么写.

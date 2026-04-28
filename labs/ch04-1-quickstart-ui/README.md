# Ch 4.1 · DeepAgents 快速开始 + Gradio UI

> "像 Spring Boot 一样三参数启动 Agent" — 然后给它一个网页对话界面.
>
> 心智模型 ref: [Karpathy — LLM OS](../../docs/references/big-names/01-karpathy.md) · DeepAgents 是 LLM OS 视角的具象化 (内核 + 工具 + 文件系统 + 子进程).

## 学完能力

- 5 分钟用 `create_deep_agent` 启动一个 Deep Agent
- 给 Agent 接一个真实搜索工具
- 套上 Gradio 网页 UI, 让用户可对话 + 看 Agent 的思考过程

## Spring Boot 类比图

```
@SpringBootApplication                  create_deep_agent(model, tools, system_prompt)
   │                                       │
   ├── starter 自动装配 Web/JPA/...        ├── 自动装配 Planning Tool (write_todos)
   ├── @Bean 配置                          ├── 自动装配 Virtual FS (read_file/write_file/...)
   └── 一行 SpringApplication.run()        └── 自动装配 SubAgent 派发能力
```

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_quickstart.py` | 三参数最小 demo (CLI) | `python src/01_quickstart.py` |
| `02_with_search.py` | 加联网搜索工具 | `python src/02_with_search.py` |
| `03_gradio_ui.py` | + Gradio 网页对话 (含中间过程展示) | `python src/03_gradio_ui.py` → 浏览器打开 http://localhost:7860 |

## 一键验证

```bash
bash verify.sh
```

CLI 脚本 (01/02) 真调 LLM, Gradio (03) 启动 → curl health → kill.

## 关键 API 速查

```python
from deepagents import create_deep_agent
from common.llm import get_llm

agent = create_deep_agent(
    model=get_llm(),
    tools=[my_tool_1, my_tool_2],     # 你的自定义工具
    system_prompt="你是...你的工作流程...",  # 长指令模板
)

# 调用
result = agent.invoke({"messages": [HumanMessage(content="你的问题")]})
print(result["messages"][-1].content)
print(result.get("files"))   # 看看虚拟 FS 里有啥
```

## 内置工具 (DeepAgents 自动给的, 不用你写)

| 类别 | 工具 | 用途 |
|---|---|---|
| Planning | `write_todos` | LLM 列任务清单 + 标记状态 |
| File System | `read_file` | 读虚拟 FS 文件 |
| | `write_file` | 写虚拟 FS 文件 |
| | `edit_file` | 编辑文件 (类似 patch) |
| | `ls` | 列目录 |
| | `glob` | 通配符匹配 |
| | `grep` | 内容搜索 |

## 下一步

学完 Ch4.1 → 进 [Ch 4.2.1 多层记忆](../ch04-2-1-memory/) 把 Agent 加上记忆.

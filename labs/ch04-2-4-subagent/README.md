# Ch 4.2.4 · SubAgent 编排

> 一个 Agent 干不完的事, 让多个专家 Agent 协作 — 主 Agent 派活, SubAgent 干活.

## 学完能力

- 用 `subagents=[...]` 参数声明子 Agent 队伍
- 主 Agent 用 `task` 工具自动派发任务给合适的 SubAgent
- 理解 SubAgent 上下文隔离的好处

## 三角色协作场景

```
            主 Agent (Project Manager)
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   研究员          批评家         写手
   Researcher     Critic        Writer
   (用搜索工具)    (审稿,挑刺)   (整理 markdown)
```

## 脚本列表

| 脚本 | 主题 | 跑法 |
|---|---|---|
| `01_three_role_agent.py` | 主 + 研究员 + 批评家 + 写手 4 个 Agent 协作 | `python src/01_three_role_agent.py` |
| `02_isolated_context.py` | SubAgent 上下文隔离演示 | `python src/02_isolated_context.py` |
| `03_recursive_subagent.py` | SubAgent 派生 SubAgent (树形分工) | `python src/03_recursive_subagent.py` |

## 一键验证

```bash
bash verify.sh
```

## 关键 API

```python
from deepagents import SubAgent, create_deep_agent

researcher = SubAgent(
    name="researcher",
    description="负责搜索资料 + 总结要点. 当需要联网调研时派给我.",
    system_prompt="你是研究员, 用 web_search 搜 1-2 次, 把要点列成 bullet.",
    tools=[web_search],     # 可选, 不传则继承主 agent
)

critic = SubAgent(
    name="critic",
    description="审稿 + 挑刺. 当需要质量把关时派给我.",
    system_prompt="你是审稿人, 找出文章的 3 个改进点 (论据/逻辑/可读性).",
)

writer = SubAgent(
    name="writer",
    description="把零散素材整理成 markdown. 当需要正式输出时派给我.",
    system_prompt="你是写手, 把素材整成结构化 markdown.",
)

main_agent = create_deep_agent(
    model=get_llm(),
    tools=[web_search],
    system_prompt="你是项目经理. 用 task 工具派给 researcher/critic/writer.",
    subagents=[researcher, critic, writer],
)

result = main_agent.invoke({"messages": [HumanMessage(content="...")]})
```

## SubAgent 上下文隔离

| 主 Agent 看到 | SubAgent 看到 |
|---|---|
| 全部历史 messages + 工具调用 | 只看到自己的子任务 + 自己的 messages |
| Token 总量大 | Token 总量小 |
| 容易"上下文中毒" | 干净的工作环境 |

## 下一步

学完 SubAgent → 进 [Ch 4.3 总结](../ch04-3-summary/) 端到端 demo + 全功能 Gradio UI.

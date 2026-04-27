# Ch 3 · 框架对比 — LangChain vs LangGraph vs DeepAgents

> 同一个研究任务用三种框架实现, 看清各自的"段位"和适用场景.

## 任务定义

**研究助手**: 给定一个研究问题, Agent 自动:
1. 用搜索工具联网找资料
2. 综合多源信息
3. 输出一份结构化研究报告

例如:
```
> Q: "DeepAgents 和 LangChain 普通 Agent 的区别?"
> A: # 研究报告
     ## 关键差异
     1. ...
     ## 应用场景对比
     ...
```

## 三种实现对比

| 文件 | 框架 | 代码量 | 看点 |
|---|---|---|---|
| `01_langchain_only.py` | 纯 LangChain | ~150 行 | 链式拼装, 手动管循环, 控制力最强 |
| `02_langgraph.py` | LangGraph | ~180 行 | 状态机, 节点/边显式, 支持断点续跑 |
| `03_deepagents.py` | DeepAgents | ~50 行 | 三参数启动, 自动 Planning + 文件系统 |

## 学完能力

- 看到一个 LLM 应用需求, 能选对框架
- 理解 LangChain → LangGraph → DeepAgents 是"抽象层级递增"
- 知道为什么 DeepAgents 是 "Spring Boot of Agents"

## 一键验证

```bash
bash verify.sh
```

注意: 三个脚本都会真实联网搜索 + 调 LLM, 各跑一次约 30-60 秒.

## 总结对照

| 维度 | LangChain | LangGraph | DeepAgents |
|---|---|---|---|
| 抽象层级 | 低 (积木) | 中 (状态机) | 高 (脚手架) |
| 上手难度 | 中 | 高 | 低 |
| 控制粒度 | 高 | 高 | 中 (用默认即可) |
| 适合场景 | 自定义流程 | 复杂多步任务 | 标准 Agent 需求 |
| Spring 类比 | Spring Framework | Spring StateMachine | Spring Boot Starter |
| 一行启动? | ❌ | ❌ | ✅ |
| 自带 Planning? | ❌ | ❌ | ✅ |
| 自带文件系统? | ❌ | ❌ | ✅ |
| 自带 SubAgent? | ❌ | ❌ | ✅ |

## 下一步

学完 Ch3 → 进 [Ch 4.1 DeepAgents 快速开始](../ch04-1-quickstart-ui/) 体验"一行启动".

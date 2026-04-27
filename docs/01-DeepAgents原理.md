# DeepAgents 原理 — Spring Boot 类比版

> 用 Java 工程师最熟的 Spring 类比, 讲清 DeepAgents 是个啥.

## 1. 一句话定位

> **LangChain 是 LLM 时代的 Spring**, **LangGraph 是 LLM 时代的 Spring StateMachine**, **DeepAgents 是 LLM 时代的 Spring Boot Starter for Agents**.

## 2. 三层抽象图

```
┌─────────────────────────────────────────────────────────────┐
│ L3 · 约定优于配置脚手架                                      │
│      DeepAgents (create_deep_agent + 内置 4 件套)           │
│                                                             │
│      类比: Spring Boot Starter (spring-boot-starter-*)      │
├─────────────────────────────────────────────────────────────┤
│ L2 · 状态机 / 编排                                           │
│      LangGraph (StateGraph + Checkpointer + add_messages)   │
│                                                             │
│      类比: Spring StateMachine + Spring Integration         │
├─────────────────────────────────────────────────────────────┤
│ L1 · 核心抽象                                                │
│      LangChain (LLM / Tool / Chain / Memory / LCEL)         │
│                                                             │
│      类比: Spring Framework (IoC / AOP / 核心容器)          │
└─────────────────────────────────────────────────────────────┘
```

## 3. DeepAgents 内置 4 件套

```python
# 你写这一行
agent = create_deep_agent(model, tools, system_prompt)

# 等价于自动装配了 4 个能力:
#
#   1. Planning Tool (write_todos)
#       LLM 自管 todo 清单, 标记 in_progress / completed
#       → 类似 @Async 的任务拆解能力
#
#   2. Virtual File System
#       内置 read_file / write_file / edit_file / ls / glob / grep
#       → 类似 Spring Batch 的中间存储 (避免 messages 爆炸)
#
#   3. SubAgent
#       通过 task() 工具派发子任务给专家 Agent
#       → 类似 @Async 的 Future 派发, 加上独立上下文隔离
#
#   4. Detailed System Prompt
#       内置 ~2000 字长指令模板, 教 LLM 如何用上面 3 件套
#       → 类似 @SpringBootApplication 的默认配置
```

## 4. 关键 API 对照

| Spring | DeepAgents |
|---|---|
| `@SpringBootApplication` | `create_deep_agent(model, tools, system_prompt)` |
| `@Bean ChatClient` | `ChatTongyi(model="qwen-plus")` |
| `@RestController public class C { @GetMapping(...) }` | LangGraph StateGraph 节点 |
| `@Configuration class Config { @Bean }` | RunnableConfig |
| `@Aspect public class LogAspect { @Before(...) }` | LangChain Callbacks / LangSmith |
| `Spring Data JPA Repository` | `VectorStore` / `Retriever` |
| `@Transactional` | LangGraph Checkpointer |
| `@Async public void backgroundTask()` | DeepAgents `subagents=[...]` |
| `application.yml` profile | `.env` + `LLM_PROVIDER` |
| `pom.xml`: `spring-boot-starter-web` | `pip install deepagents` |

## 5. 何时用什么

```
任务复杂度  →   推荐方案
─────────────────────────────────
简单单步 LLM 调用     → ChatTongyi.invoke (LangChain L1)
多步链式处理          → LCEL `prompt | llm | parser` (L1)
状态机 / 断点续跑     → LangGraph StateGraph (L2)
标准 ReAct Agent      → langgraph create_react_agent (L2)
长任务 + 计划 + FS    → DeepAgents create_deep_agent (L3)
多角色协作            → DeepAgents + subagents (L3)
```

## 6. DeepAgents 的"长出来" — 为什么需要它?

**痛点**: 普通 Agent 跑长任务时:
- messages 越来越长, token 爆炸
- 多个工具调用结果混在一个上下文里, 上下文中毒
- LLM 容易忘记最初目标
- 没有显式的 todo / 进度追踪

**DeepAgents 的解法**:
1. **Planning Tool**: 把目标显式列成 todo, LLM 跟着 todo 推进
2. **Virtual File System**: 中间结果落"虚拟盘", 主 messages 保持简洁
3. **SubAgent**: 派子任务给专家, 子任务的中间过程不污染主 Agent
4. **Detailed System Prompt**: 内置长指令教 LLM 如何用上面 3 件套

## 7. 实战路线 — 从 Spring 到 DeepAgents

如果你是 Java/Spring 工程师, 推荐学习顺序:

1. **Ch1 Python 基础** — 把语法切换到 Python (从 `public static void main` 到 `if __name__ == "__main__":`)
2. **Ch4.1 DeepAgents Quickstart** — 直接用最熟悉的"Spring Boot Starter"心智, 三参数启动 Agent
3. **Ch2 LangChain 基础** — 回头补 LCEL / Tool / Memory 的"乐高积木"
4. **Ch3 框架对比** — 看清 LangChain → LangGraph → DeepAgents 的层级
5. **Ch4.2.x 各功能** — 深入记忆 / 意图 / 工具+RAG / SubAgent 的工程实践

这条路径让你 **第 2 步就能跑出可演示的 demo**, 后面慢慢补理论, 不会卡在"Python 基础 → LangChain 一切" 这种线性学法上.

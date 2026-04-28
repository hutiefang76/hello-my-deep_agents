# Ch 9 · Cognitive Architecture 实战 — L1→L5 演化

> **主线终章** (Mainline Finale): 把 Chase 5 级阶梯落到一个**真业务**, 完整看一次演化.
>
> **Chase 核心洞见** (Key Insight, Harrison Chase, LangChain):
> *"Own your cognitive architecture, outsource agent infrastructure. Cognitive architecture is your moat."*
>
> **中文翻译**: 拥有你的认知架构, 外包智能体基础设施. 认知架构才是你的护城河.

---

## 真业务 · E-commerce Customer Service Bot (电商客服机器人)

**业务场景** (Business Scenario):
- 电商平台客服, 处理 8 类咨询: 退货 / 物流 / 支付 / 会员 / 优惠券 / 投诉 / FAQ / 闲聊
- 单日并发 10K+ 工单, 70% 简单问题应**用最低级**搞定 (省成本)
- 30% 复杂问题需要**最高级 Agent**介入 (保质量)

**演化目标**: 同一业务从 L1 硬编码到 L5 自主 Agent, 看清:
- 每升一级**多解决了什么问题**
- 每升一级**多花了多少成本**
- **何时该升级 / 何时该降级**

---

## 5 阶段 (5 Stages)

| Stage | English | 中文 | 实现 | 处理上限 | 单 query 成本 |
|---|---|---|---|---|---|
| **L1** | Hardcoded FAQ | 硬编码 FAQ | if-else 关键词匹配 | 仅固定问题 | 0 (免费) |
| **L2** | Single LLM Call | 单 LLM 调用 | 直接 LLM + system prompt | 通用闲聊+简答 | ¥0.001 |
| **L3** | LLM Chain (Workflow) | LLM 链 (工作流) | Intent → Retrieve → Respond | + RAG 知识库问答 | ¥0.003 |
| **L4** | LLM Router | LLM 路由 | 5 意图各走不同 sub-chain | + 复杂场景分流 | ¥0.005 |
| **L5** | Autonomous Agent | 自主 Agent | DeepAgent + Reflection + Tools | + 多步任务 (退款/查单+改单) | ¥0.020+ |

---

## 学完能力 (Learning Outcomes)

- 拿到一个真业务, 能立刻规划"该用哪一级 / 渐进升级路径"
- 理解 Chase 论点: **Cognitive Architecture (业务决策树) ≠ Agent Infrastructure (LangGraph 等)**
- 知道**什么时候该降级** (L5 也不是万能, 简单问题用 L1 更对)

## 脚本列表

| 脚本 | 阶段 | 内容 |
|---|---|---|
| `01_l1_hardcoded.py` | L1 | if-else FAQ + 关键词匹配 |
| `02_l2_single_call.py` | L2 | 单 LLM + 长 system prompt |
| `03_l3_chain_workflow.py` | L3 | Intent → Retrieve → Respond chain |
| `04_l4_router.py` | L4 | 8 意图各走不同 handler |
| `05_l5_autonomous_agent.py` | L5 | DeepAgent + 全工具 + Reflection |
| `06_evolution_compare.py` | All | 同一组 query 跑全部 5 级, 对比 |

## 一键验证

```bash
bash verify.sh
```

## Chase 论点深度解读 (Key Argument)

**Outsource (该外包的, 框架做)**:
- LangGraph StateGraph 编排
- DeepAgents 内置工具 (write_todos, write_file, ls)
- Checkpointer 持久化
- Trace / Eval 基础设施

**Own (该自己拥有的, 业务护城河)**:
- 哪些问题用 L1 / L2 / L3 / L4 / L5 (你的成本-质量决策)
- 业务规则 (退款政策 / 合规红线 / 会员等级权益)
- Prompt 工程 (你的 tone of voice / 行业术语)
- 评估标准 (你的"好回复"长什么样)
- Guardrails 配置 (你的红线词列表)

> **一句话**: 框架是 commodity, **业务认知是你的核心资产**.

## 何时该升级 / 降级

```
L1 → L2: 关键词匹配开始覆盖不了用户口语化表达 (eg "我那双鞋开胶了")
L2 → L3: 简答开始不够, 需要查 KB / 处理多步逻辑
L3 → L4: chain 开始臃肿, 8+ 意图全塞一个 prompt 效果差
L4 → L5: 出现"不可枚举的复杂任务" (eg "查单+改单+发券+通知物流")

降级信号 (Anti-pattern):
  - L5 处理 "你好" → 浪费, 应该 L1
  - 60% 流量集中在 5 类 FAQ → 应该 L1+L2 兜底, L5 只接其余 40%
```

## 下一步 (After This Course)

- 把课程框架带到你的真业务 (不是再写 demo)
- 接 LangSmith 看 trace (生产可观测性)
- 接 Anthropic Skills (新趋势, 让 Agent 学习自定义工作流)
- 上 MCP (跨生态打通)
- 接多模态 (qwen-vl-plus / qwen-tts)

## 参考

- [Harrison Chase — Cognitive Architecture (LangChain Blog)](https://blog.langchain.com/what-is-a-cognitive-architecture/)
- [Chase — Own architecture, outsource infrastructure](https://blog.langchain.com/why-you-should-outsource-your-agentic-infrastructure-but-own-your-cognitive-architecture/)

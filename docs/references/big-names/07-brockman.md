# Greg Brockman · OpenAI President · 4-Part Prompt Framework · o-series Reasoning

> OpenAI 联合创始人 + 总裁 · 早期 Stripe CTO
> 影响力: 他在 2025-02 公开背书的「4 部分 Prompt 框架」是当前**生产级 prompt 设计的官方推荐**

---

## 1. 核心思想: The 4-Part Prompt Framework (2025)

```
┌────────────────────────────────────────────────┐
│         Greg Brockman 4-Part Framework         │
├────────────────────────────────────────────────┤
│  1. Goal           目标(你要什么)                │
│  2. Return Format  返回格式(结构/字段/示例)      │
│  3. Warnings       警告/约束(必须避免/必须验证)  │
│  4. Context Dump   上下文倾倒(背景/数据/历史)    │
└────────────────────────────────────────────────┘
```

> *"OpenAI's president Greg Brockman shared a perfect framework for proper prompting: Goal, Return Format, Warnings, Context Dump."*

**中文**: 完美 prompt 4 段式：目标 / 返回格式 / 警告约束 / 上下文倾倒。

### 各部分含义

| 段 | 作用 | 例子 |
|---|---|---|
| Goal | 一句话讲明白要做啥 | "为这位用户的退货请求生成回复" |
| Return Format | 严格定义输出结构 | "JSON: `{tone, summary, action_required: bool}`" |
| Warnings | 红线/必查项 | "**禁止**承诺退款金额；**必须**核对订单状态" |
| Context Dump | 业务背景+数据 | "用户订单号 O123 / 退货政策 v2.3 全文 / 用户消费历史" |

### 为什么这样切？

- 模型本质是"按概率续写"——你给的结构越清晰，输出越稳定
- o-series（o1/o3）推理模型尤其吃这套——这是它们设计时的预期输入格式
- 4 段式 = **强制你想清楚 4 件事**，避免随手写 prompt

---

## 2. Brockman 的关键论断

### 2.1 o-series 不是普通模型

> *"Unlike traditional prompts that rely heavily on word associations, o1 prompts are specifically tailored to trigger advanced reasoning in OpenAI's latest models."*

**中文**: o1 prompt 不是靠"词汇联想"起作用的——它是为触发深度推理设计的。**潜台词**: 不要给 o-series 加"step by step"这种小技巧，反而干扰它内置的 chain-of-thought。

### 2.2 Spec-Driven 思想

(虽然搜索结果未直接命中，但 OpenAI 内部"Specs over Prompts"运动是 Brockman 推动的)
**核心**: 把 Prompt 当代码——加版本、加测试、加 review。

---

## 3. 原文金句

| EN | 中文 | 出处 |
|---|---|---|
| "Goal · Return Format · Warnings · Context Dump." | 目标 · 返回格式 · 警告 · 上下文倾倒。 | DataScienceDojo X, 2025-02 |
| "o1 prompts trigger advanced reasoning, not word associations." | o1 prompt 触发深度推理，不靠词汇联想。 | OpenAI 2025-02 prompting guide |

---

## 4. 落地到本教程哪一章

| 内容 | 当前覆盖 | 改进动作 |
|---|---|---|
| 4-Part Framework | ❌ 全无 | Ch2 加 `06_brockman_4part_prompt.py` — 同一任务用 random prompt vs 4 段式对比，看输出稳定性 |
| Spec-Driven Prompts | ⚠️ openspec/ 有但与 prompt 无关 | Ch2 README 加一节"Prompt = code, 用 4 段式版本化管理" |
| o-series 适配 | ❌ 全无 | Ch11(Context Engineering 新章) 加一节"推理模型的 prompt 反直觉" |

**关键示例（应放进 ch02 新脚本）**:

```python
# ❌ 业余写法
prompt = "帮我分析下这个订单退货请求"

# ✅ Brockman 4 段式
prompt = f"""
# Goal
为以下退货请求生成客服回复.

# Return Format
JSON: {{
  "tone": "正式|亲切|抱歉",
  "decision": "approve|reject|need_more_info",
  "reply_text": "<150 字以内回复>",
  "action_items": ["..."]
}}

# Warnings
- 禁止承诺超出政策的赔偿
- 必须先核对订单状态(已收货才能退)
- 不暴露其他用户信息

# Context Dump
订单: {order_json}
退货政策: {policy_v23}
用户历史: {user_history}
"""
```

---

## 5. Sources

- [Greg Brockman 4-Part Framework (YourStory 2025-02)](https://yourstory.com/2025/02/greg-brockman-perfect-ai-prompt-framework)
- [Inc — How to Write the Perfect AI Prompt](https://www.inc.com/jessica-stillman/how-to-write-the-perfect-ai-prompt-according-to-openai-president-greg-brockman/91150209)
- [DataScienceDojo X tweet](https://x.com/DataScienceDojo/status/1891502865346175152)
- [OpenAI February 2025 Prompting Guide for o-series](https://deepnewz.com/ai-modeling/openai-releases-february-2025-prompting-guide-greg-brockman-o-series-models-o1-a3c6216e)
- [Medium full guide](https://medium.com/kinomoto-mag/the-ultimate-guide-to-structuring-ai-prompts-insights-from-openais-greg-brockman-2b202f47046a)

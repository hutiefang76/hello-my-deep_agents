# OpenSpec 方法论 — Spec-Driven Development

> 让 AI 编码助手"先看规约, 再写代码", 而不是 vibe coding.

## 1. 是什么

OpenSpec 是个轻量框架, 把以下东西放进 `openspec/` 目录:

```
openspec/
├── project.md                  # 项目宪章 (使命/信条/范围)
├── AGENTS.md                   # AI agent 工作准则 (红线/规范)
└── specs/
    └── <capability>/
        └── spec.md             # 这个 capability 的 Must/Should/Could
```

特点:
- **Markdown only** — 不引入新语法, AI 工具天然能读
- **三态机** — proposal → apply → archive
- **Delta markers** — 跟踪 ADDED / MODIFIED / REMOVED 的变更
- **不绑定特定 AI 工具** — Claude Code / Cursor / Copilot / Gemini 都能用

## 2. 在本项目怎么用

每个 lab 的关键 capability 对应一份 spec, 例如:

- `openspec/specs/llm-provider-abstraction/spec.md` — common/llm.py 的规约
- `openspec/specs/multi-layer-memory/spec.md` — Ch4.2.1 多层记忆规约
- `openspec/specs/intent-routing/spec.md` — Ch4.2.2 意图识别规约

每份 spec 含三档要求:
- **Must** — 必须满足
- **Should** — 应该满足
- **Could** — 可以但非必须

## 3. 三态机流程

```
┌─────────────┐    ┌─────────┐    ┌──────────────────┐
│ proposal    │ →  │ apply   │ →  │ archive          │
│ (changes/)  │    │ (实施)   │    │ (specs/)         │
└─────────────┘    └─────────┘    └──────────────────┘
       ↓                ↓                  ↓
  写提案文档          写代码                spec 标 Implemented
  团队/AI 审查        跑测试               移到 specs/ 目录
```

## 4. 一份 spec 的标准模板

```markdown
# Spec: <capability-name>

> 一句话说明这个 capability 解决什么问题

**Status**: Pending / Implementing / Implemented
**Related lab**: labs/chXX-xxx/

## Why
为什么需要这个 capability

## Requirements

### Must
1. M1: ...
2. M2: ...

### Should
1. S1: ...

### Could
1. C1: ...

## Verification
怎么验证 spec 已满足

## Implementation Notes
关键设计决策

## Related Decisions
记录关键 tradeoff (为什么不用 X / 为什么选 Y)
```

## 5. 为什么有用

**对 AI 编码助手**:
- 不再"凭感觉写代码", 而是先读 spec 再下手
- 修改时知道"什么不能动" (Must), "什么可以优化" (Should/Could)
- 多个 AI 工具协作时有共同的 source of truth

**对人**:
- code review 时直接看 spec, 不用反复讲需求
- 跨人交接时, spec.md 是"我期望的行为"的契约
- 重构时知道"什么是对的", 防过度重构

## 6. 与 superpowers 配合

OpenSpec 是 **"做什么 (What)"** 的契约, superpowers 是 **"怎么做 (How)"** 的方法论:

```
brainstorm  ← 用 superpowers 探索需求
   ↓
write spec  ← 用 OpenSpec 落契约
   ↓
write plan  ← 用 superpowers 拆步骤
   ↓
execute     ← 写代码 + 跑测试
   ↓
verify      ← 用 superpowers verification-before-completion
   ↓
archive     ← OpenSpec 标 Implemented
```

## 7. 参考

- 官网: https://openspec.dev
- GitHub: https://github.com/Fission-AI/OpenSpec
- 本仓库的实践: 见 [openspec/](../openspec/)

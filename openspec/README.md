# OpenSpec 目录

> Spec-Driven Development 的规约仓库.

## 结构

```
openspec/
├── project.md                       # 项目宪章 (使命/信条/范围/技术栈)
├── AGENTS.md                        # AI agent 工作准则 (代码规范/红线)
├── specs/                           # 各 capability 规约 (实现完成的)
│   └── <capability-name>/
│       └── spec.md                  # Must / Should / Could
└── changes/                         # 提案中的变更 (实现前)
    └── <change-name>/
        ├── proposal.md              # 提议做什么
        ├── design.md                # 怎么设计
        └── tasks.md                 # 拆解成的小任务
```

## 三态机

```
proposal  →  apply  →  archive
   ↓           ↓          ↓
[changes]  [实现中]   [specs]
```

1. **Proposal**: 在 `changes/` 写提案, 团队/AI 审查
2. **Apply**: 实施 (写代码 + 跑测试)
3. **Archive**: 完成后从 `changes/` 移到 `specs/`, spec.md 顶部标 `Status: Implemented`

## 当前 Capabilities

| Spec | 状态 | 文件 |
|---|---|---|
| LLM Provider Abstraction | Implemented | `specs/llm-provider-abstraction/spec.md` |
| Multi-Layer Memory | Pending (Commit #7) | `specs/multi-layer-memory/spec.md` |
| Intent Classification & Routing | Pending (Commit #8) | `specs/intent-routing/spec.md` |
| Tools & RAG Pipeline | Pending (Commit #9) | `specs/tools-rag/spec.md` |
| SubAgent Orchestration | Pending (Commit #10) | `specs/subagent-orchestration/spec.md` |

## 怎么写 Spec

模板:

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
```

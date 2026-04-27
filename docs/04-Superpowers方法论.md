# Superpowers 方法论 — Claude Code 的工作准则

> Claude Code 团队提炼的"AI 编码工作流", 让 AI 工具不"乱来".

## 1. 核心 4 阶段

```
brainstorm → writing-plans → executing-plans → verification-before-completion
   ↓               ↓                ↓                        ↓
  对齐需求       拆解步骤         写代码                   交付前验证
```

## 2. 每阶段的"硬规则"

### 2.1 Brainstorm (探索需求)

- **One question at a time** — 不堆问题
- **Multiple choice preferred** — 给选项比开放题好
- **YAGNI ruthlessly** — 砍不必要的 feature
- **HARD-GATE** — 用户没批准设计前不下手实施

### 2.2 Writing-Plans (拆解步骤)

- 每个里程碑独立可验证
- 每步含"做什么 + 怎么验证"
- 标明依赖关系

### 2.3 Executing-Plans (执行)

- 一次只做一个 todo
- 完成立即标 completed (不批量)
- 遇到阻塞 → 创建新 todo 描述阻塞

### 2.4 Verification-Before-Completion (验证)

- 不说"应该能跑" → 必须真跑
- 不说"按理来说" → 必须贴出证据
- 在 commit / PR 前跑 build + test

## 3. 在本项目怎么用

每个 lab 的开发节奏遵循 4 阶段:

1. **Brainstorm**: 在主仓库 docs/00-课程设计.md 已对齐总骨架
2. **Plan**: 每个 lab 的 README.md 即 plan (学完能力 + 脚本列表)
3. **Execute**: 写 src/*.py 代码
4. **Verify**: bash verify.sh 跑通, commit message 含 `Verify:` 段落

## 4. 红线 (Hard Rules)

碰了直接 revert:

1. **🚫 严禁明文 key** — `.env` 必须 gitignore, 任何 key 不进 commit
2. **🚫 严禁未验证的 commit** — `python -m py_compile` + 真跑过
3. **🚫 严禁破坏性 git 操作** — 不 `--force`, 不 `reset --hard`
4. **🚫 严禁超范围修改** — 一次 commit 一个里程碑

详见 [openspec/AGENTS.md](../openspec/AGENTS.md).

## 5. 方法论协同图

```
┌──────────────────────────────────────────────────────┐
│ OpenSpec — "做什么" 的契约                            │
│   project.md / AGENTS.md / specs/<cap>/spec.md       │
└──────────────────────────────────────────────────────┘
                       ▲
                       │ 引用
┌──────────────────────────────────────────────────────┐
│ Superpowers — "怎么做" 的方法论                       │
│   brainstorm → plan → execute → verify               │
└──────────────────────────────────────────────────────┘
                       ▲
                       │ 实施于
┌──────────────────────────────────────────────────────┐
│ Codebase — labs/ + common/ + scripts/                │
│   每 commit 一个里程碑, 全部 verify.sh 跑通           │
└──────────────────────────────────────────────────────┘
```

## 6. 为什么这样设计

**Without 方法论**:
- AI 一上来写代码, 后来发现需求理解错了
- 写完不验证, "应该能跑" 但其实没跑过
- 一次 commit 改几十个文件, 没法 review
- 凭记忆改代码, 错了不知道是谁的责任

**With 方法论**:
- brainstorm 阶段先对齐, 减少返工
- 每步显式 verify, 没贴证据的 commit 不算完成
- 每 commit 一个里程碑, 出问题能 revert 到上一里程碑
- spec 是 source of truth, AI 和人都按这个干

## 7. 参考

- Superpowers GitHub: https://github.com/anthropics/superpowers
- Anthropic 工程博客: https://www.anthropic.com/engineering

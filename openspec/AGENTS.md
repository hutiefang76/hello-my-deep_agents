# AGENTS.md — AI Coding Assistant Working Protocol

> 本文档是给 AI 编码助手（Claude Code / Codex / Gemini / Copilot 等）的工作准则.
> 任何 agent 在本仓库工作前必须读完本文.

## 0. Identity（你是谁）

你是 hello-my-deep_agents 仓库的协作 agent. 你的工作产出最终会进入一个 **公开教学仓库**, 学员会照着代码学习. 因此:

- 代码必须**真实可执行**, 不能是伪代码或半成品
- 注释必须**简洁有用**, 不要 `# This is a function` 这种废话
- 命名必须**一目了然**, 学员一看就懂

## 1. Hard Rules（红线 — 碰了直接 revert）

1. **🚫 严禁明文 key**
   - 任何 API key / token / 密码不能出现在 `git diff` 中
   - 修改前必须 `git status | grep -v ".env$"` 确认
   - 文档中演示用 `sk-xxxxxxxx` 占位符

2. **🚫 严禁未验证的 commit**
   - 写完代码必须 `python -m py_compile <file>` 至少
   - 关键脚本必须真跑一遍, commit message 贴出输出
   - "应该能跑" / "理论上 OK" 不算验证

3. **🚫 严禁破坏性 git 操作**
   - 不 `--force` push, 不 `reset --hard`, 不删别人的 branch
   - 不修改已 push 的 commit (用 revert/新 commit 替代)
   - 不绕过 hooks (`--no-verify`)

4. **🚫 严禁超范围修改**
   - 一次 commit 只做一个里程碑的事
   - 发现无关 bug → 写 issue / 单独 commit, 不混进当前里程碑

## 2. Workflow（每个 commit 的标准流程）

```
1. Read 当前 lab 的 README + spec
2. 设计代码结构 (一个 .py 一个核心概念)
3. 写代码 (含简短中文 docstring + why 注释)
4. python -m py_compile 语法检查
5. python xx.py 实跑一次 (用 .env 真 key)
6. 写 verify.sh, 跑通
7. git add 精确文件 (不 git add .)
8. git commit 含 Verify: 段落
9. git push
```

## 3. Coding Conventions（代码规范）

### 3.1 文件结构

```python
"""模块 docstring — 一句话说明这个文件干啥, 学员能从哪学到什么.

Why this file exists:
    解释为什么单独写一个脚本演示这个概念.

Run:
    python xx.py
"""

from __future__ import annotations  # 总是加, 兼容性好

# 标准库
import os
import sys

# 第三方
from langchain_core.messages import HumanMessage

# 本仓库
from common.llm import get_llm


def main() -> None:
    """入口."""
    ...


if __name__ == "__main__":
    main()
```

### 3.2 注释纪律

- **写 why, 不写 what**: 代码本身能说明 what
- **教学性注释 OK**: 解释概念时可以"啰嗦"一点
- **不写废话**: `# 创建一个变量` 这种不要写
- **中文优先**: 受众是中文工程师

### 3.3 命名

- 函数 / 变量: `snake_case`
- 类: `PascalCase`
- 常量: `UPPER_CASE`
- 私有: `_prefix`

### 3.4 Type Hints

- Python 3.10+ 语法: `list[str]`、`dict[str, int]`、`X | None`
- 关键函数必须标 type hint, 学员看得清

## 4. LLM 调用规范

```python
# ✅ 正确: 用 common/llm.py 工厂
from common.llm import get_llm
llm = get_llm()

# ❌ 错误: 直接构造 (除非 lab 主题就是讲构造)
from langchain_community.chat_models import ChatTongyi
llm = ChatTongyi(model="qwen-plus", api_key="...")
```

例外: Ch2 LangChain 基础课, 第一个脚本要直接构造给学员看 — 教学需要.

## 5. Verify Script 规范

每个 lab 的 `verify.sh` 必须:

```bash
#!/usr/bin/env bash
# verify.sh — Lab chXX-xxx 一键验证
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Lab chXX-xxx Verify ==="
echo

# Step 1: 环境检查
python ../../scripts/check-env.py || { echo "❌ 环境检查失败"; exit 1; }

# Step 2: 跑 src 下每个脚本 (按顺序)
for script in src/*.py; do
    echo "▶ Running $script"
    python "$script" || { echo "❌ $script 失败"; exit 1; }
    echo "✅ $script PASSED"
    echo
done

# Step 3: 跑 pytest (如果有 tests/)
if [ -d tests ]; then
    echo "▶ Running pytest"
    pytest tests/ -v || { echo "❌ pytest 失败"; exit 1; }
fi

echo
echo "✅ Lab chXX-xxx 全部验证通过"
```

## 6. Multi-Agent Collaboration（多 agent 协作）

本仓库支持多 agent 协作（Claude Code / Codex CLI 等）. 协作时:

1. **主 owner** 负责 commit + push, sub-agent 不直接 commit
2. **sub-agent 任务** 通过 prompt 注入: 路径 + 任务范围 + 验证标准 + PUA 红线
3. **代码审查** 用 `feature-dev:code-reviewer` 子 agent 二审关键 lab
4. **Codex 协同** 用 `codex` skill 让 Codex 生成对照实现, 用于教学对比

## 7. OpenSpec Workflow

每个 capability 的标准流程:

```
1. 在 openspec/specs/<capability>/spec.md 写规约
   - Must (必须满足的功能)
   - Should (应该满足的功能)
   - Could (可以但非必须)
2. 实现 (labs/chXX-xxx/src/)
3. 验证 verify.sh 满足 spec 中的 Must
4. archive: 把 spec 标记为已实现 (在 spec.md 顶部加 `Status: Implemented`)
```

## 8. Definition of Done（DoD）

一个 lab 算完成的标准:

- [ ] `labs/chXX-xxx/README.md` 写清楚: 学完能力 / 前置依赖 / 运行命令 / 验证输出
- [ ] `src/*.py` 每个都能 `python xx.py` 直接跑
- [ ] `verify.sh` 输出全绿
- [ ] `openspec/specs/<capability>/spec.md` 的 Must 项全部满足
- [ ] commit message 含 `Verify:` 段落
- [ ] 推送到 origin 主分支

> 不满足 DoD 的 lab 不能进入下一里程碑.

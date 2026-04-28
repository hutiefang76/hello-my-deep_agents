# Docker 部署指南 — 跨平台一键启动

> 任何电脑只要装了 Docker (macOS / Windows / Linux), 30 秒跑通课程.

## 1. 前置条件 (Prerequisites)

| 平台 | Docker 安装 |
|---|---|
| **macOS** | Docker Desktop: https://docs.docker.com/desktop/install/mac/ |
| **Windows** | Docker Desktop: https://docs.docker.com/desktop/install/windows/ (含 WSL2) |
| **Linux** | Docker Engine + Docker Compose v2: https://docs.docker.com/engine/install/ |

验证安装:
```bash
docker --version          # >= 24.0
docker compose version    # v2.x or v5.x
```

## 2. 30 秒上手

```bash
# Step 1: clone
git clone git@github.com:hutiefang76/hello-my-deep_agents.git
cd hello-my-deep_agents

# Step 2: 配 key (复制模板, 编辑填 DASHSCOPE_API_KEY)
cp .env.example .env
# 编辑 .env, 填上从 https://bailian.console.aliyun.com 申请的 sk-xxx key

# Step 3: 构建 + 启动 (首次约 5-10 分钟下载/装依赖)
make build
make up

# Step 4: 浏览器打开 Gradio UI
# Windows / macOS / Linux 都自动打开
make ui
# 或手动浏览器开: http://localhost:7861
```

---

## 3. 服务清单 (Services)

```yaml
services:
  app:       # Python 3.11 主容器 (跑 lab 脚本)
  gradio:    # Ch4.3 全功能 UI (port 7861)
  pgvector:  # PostgreSQL + pgvector (向量库)
  redis:     # 会话存储 (Memory lab)
```

```bash
# 看服务状态
make ps

# 看日志
make logs            # 全部服务
make logs-gradio     # 只看 Gradio
```

---

## 4. 跑 Lab 的几种方式

### 方式 A: 一键跑特定 lab (推荐)
```bash
make run-ch01     # Ch1 Python 基础
make run-ch05     # Ch5 决策树
make run-ch09     # Ch9 L1-L5 演化对比
make run-e2e      # Ch4.3 集大成端到端 demo
```

### 方式 B: 进容器手动跑
```bash
make shell        # 进 app 容器 bash

# 容器内:
python labs/ch04-1-quickstart-ui/src/01_quickstart.py
python labs/ch07-reflection/src/03_reflection_with_tools.py
bash labs/ch08-engineering-pillars/verify.sh
exit
```

### 方式 C: 跑全量验证
```bash
make verify-all   # 9 lab 全跑, 约 20 分钟 (真调 LLM ~50 次)

# 单个 lab 跑 verify
make verify-ch CH=ch05-workflow-vs-agent
```

---

## 5. 常用命令速查

| 命令 | 作用 |
|---|---|
| `make help` | 显示全部命令 |
| `make build` | 构建 Docker 镜像 |
| `make up` | 启动全部服务 (后台) |
| `make down` | 停服务 (保留数据) |
| `make clean` | 停 + 清数据卷 (重置) |
| `make ps` | 看服务状态 |
| `make shell` | 进 app 容器 |
| `make ui` | 浏览器打开 Gradio |
| `make check-env` | 检查 .env + LLM 调通 |
| `make doctor` | Docker 环境诊断 |

---

## 6. 故障排查 (Troubleshooting)

### 问题: build 慢 / 装依赖慢

国内访问 PyPI 慢. 已在 Dockerfile 配阿里云镜像源:
```dockerfile
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

如仍慢, 可临时改为清华源:
```bash
docker build --build-arg PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple -t deepagents-tutorial .
```

### 问题: gradio 容器启动失败

```bash
make logs-gradio   # 看具体报错
make shell         # 进 app 手动跑 python labs/ch04-3-summary/src/02_gradio_full_ui.py
```

通常是 `.env` 没配 `DASHSCOPE_API_KEY`.

### 问题: pgvector 连不上

```bash
docker compose ps pgvector   # 看健康状态
docker compose logs pgvector # 看启动日志

# 容器内连接:
make shell
psql -h pgvector -U deepagents -d deepagents   # 在容器内
```

### 问题: Windows 路径问题

如果 `volume: ./labs:/app/labs` 不生效:
- 确认 Docker Desktop 设置 → Resources → File Sharing 把项目目录加进去
- 或用 WSL2 跑 (推荐, 性能更好)

### 问题: 想换模型 (qwen-plus → qwen-max / OpenAI / Ollama)

编辑 `.env`:
```bash
LLM_PROVIDER=tongyi             # tongyi / openai_compat / ollama
LLM_MODEL=qwen-max              # 改这里
```

重启服务:
```bash
make down && make up
```

---

## 7. 不用 Docker 跑? (本地 Python)

仍然支持. 详见 [README.md](../README.md) 中"不用 Docker 直接跑"段落.

---

## 8. 镜像大小估算

```
deepagents-tutorial:latest    ~2.5 GB
  - python:3.11-slim base     ~150 MB
  - pip 依赖 (langchain etc)  ~2.0 GB (langchain + langgraph + deepagents 较大)
  - 代码 + 文档               ~50 MB
```

如需精简, 可用多阶段构建分离 build / runtime, 把 ~500MB 的 build 工具丢掉. 教学场景不优化.

## 9. 安全提醒

- `.env` 在 `.gitignore` 和 `.dockerignore` 里, **不会进镜像**
- 容器通过 `env_file: .env` 在运行时注入凭证
- 镜像可以 push 公开仓库, 不会泄漏 key

---

## 10. CI/CD 建议

GitHub Actions 跑 verify-all 模板:
```yaml
- uses: actions/checkout@v4
- run: docker compose build
- run: cp .env.example .env && echo "DASHSCOPE_API_KEY=${{ secrets.DASHSCOPE_API_KEY }}" >> .env
- run: docker compose run --rm app python -m py_compile common/llm.py
# 完整 verify-all 太慢 + 烧 token, CI 只跑 syntax check 和 1-2 个轻 lab
```

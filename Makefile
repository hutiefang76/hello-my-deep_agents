# ============================================================
# hello-my-deep_agents · Makefile
# 跨平台一键命令 (macOS / Windows-WSL / Linux 都支持)
#
# 两条路径:
#
#   推荐路径 · IDEA-first (像跑 Spring Boot 一样在 PyCharm 里跑 Python):
#     make mw-up         只起中间件 (pgvector + redis)
#     # 在 PyCharm 里右键 Run labs/chXX/src/01_xxx.py
#     make mw-down       关中间件
#
#   备选路径 · Docker 完整栈 (跨机器复现 / CI):
#     make build         构建镜像
#     make up            起全部 (app + gradio + pgvector + redis)
#     make shell         进容器跑 lab
# ============================================================

.PHONY: help setup run-configs build up down shell logs verify-all verify-ch ui clean test ps mw-up mw-down mw-logs mw-ps

DEFAULT_GOAL := help

# 中间件专属 compose 文件 (IDEA-first 路径)
MW_COMPOSE := docker-compose.middleware.yml

help: ## 显示此帮助
	@echo "hello-my-deep_agents · Make 命令"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "30 秒上手 · PyCharm-first (推荐):"
	@echo "  1. cp .env.example .env  && 编辑填 DASHSCOPE_API_KEY"
	@echo "  2. make setup                        # 一键建 .venv + 装全部依赖 (5 分钟)"
	@echo "     # Windows 用户也可双击 setup.bat"
	@echo "  3. make run-configs                  # 一键生成 62 个 PyCharm Run Config"
	@echo "  4. (可选) make mw-up                 # 起中间件 (Memory/RAG lab 用)"
	@echo "  5. 在 PyCharm 选 interpreter 为 .venv, 顶部 dropdown 选任意 lab Run"
	@echo "     详见 docs/08-PyCharm配置指南.md"
	@echo ""
	@echo "完整 Docker 路径 (备选, 跨机复现 / CI):"
	@echo "  1. cp .env.example .env  && 编辑填 DASHSCOPE_API_KEY"
	@echo "  2. make build && make up"
	@echo "  3. make ui  # http://localhost:7861"

# ===== PyCharm-first 路径: 一键 setup + run config =====

setup: ## (推荐第一步) 一键建 .venv + 装全部依赖 (5 分钟)
	@bash setup.sh 2>/dev/null || cmd //c setup.bat

run-configs: ## 批量生成 PyCharm Run Configurations (62 个)
	@.venv/Scripts/python.exe scripts/gen_run_configs.py 2>/dev/null || \
	 .venv/bin/python scripts/gen_run_configs.py

# ===== IDEA-first 路径: 只跑中间件 =====

mw-up: ## (推荐) 只起 pgvector + redis 中间件, IDEA 里跑 Python
	docker compose -f $(MW_COMPOSE) up -d
	@echo ""
	@echo "✅ 中间件已起:"
	@docker compose -f $(MW_COMPOSE) ps
	@echo ""
	@echo "下一步: 在 PyCharm/IDEA 里 Run labs/chXX/src/xx.py"
	@echo "       详见 docs/08-PyCharm配置指南.md"

mw-down: ## 关中间件 (保留数据卷)
	docker compose -f $(MW_COMPOSE) down

mw-logs: ## 跟随中间件日志
	docker compose -f $(MW_COMPOSE) logs -f

mw-ps: ## 看中间件状态
	docker compose -f $(MW_COMPOSE) ps

# ===== Docker 完整栈路径 (备选) =====

build: ## 构建 app 镜像 (Python 3.11 + 全部依赖)
	docker compose build

up: ## 启动全部服务 (后台)
	docker compose up -d
	@echo ""
	@echo "✅ 服务已启动:"
	@docker compose ps
	@echo ""
	@echo "下一步:"
	@echo "  make shell      # 进 app 容器跑 lab"
	@echo "  make ui         # 打开 Gradio UI"

down: ## 停服务 (保留数据)
	docker compose down

clean: ## 停服务 + 清数据卷 (彻底重置)
	docker compose down -v

ps: ## 查看服务状态
	docker compose ps

shell: ## 进 app 容器 bash (跑 lab 用)
	docker compose run --rm app bash

logs: ## 跟随所有服务日志
	docker compose logs -f

logs-gradio: ## 单看 Gradio 日志
	docker compose logs -f gradio

# ===== Verify 命令 =====

verify-all: ## 跑全量 9 lab verify (基础课程, 真调 LLM 约 20 分钟)
	docker compose run --rm app bash scripts/run-all-verify.sh

verify-ch: ## 跑某个 lab 的 verify (用法: make verify-ch CH=ch05-workflow-vs-agent)
	docker compose run --rm app bash labs/$(CH)/verify.sh

# ===== Lab 快速跑 =====

run-ch01: ## 跑 Ch1 Python 基础 (无需 LLM)
	docker compose run --rm app python labs/ch01-python-basics/src/01_hello_world.py

run-ch05: ## 跑 Ch5 Workflow vs Agent 决策树
	docker compose run --rm app python labs/ch05-workflow-vs-agent/src/01_decision_tree.py

run-ch09: ## 跑 Ch9 Cognitive Architecture L1-L5 演化对比
	docker compose run --rm app python labs/ch09-cognitive-arch/src/06_evolution_compare.py

run-e2e: ## 跑端到端集大成 demo
	docker compose run --rm app python labs/ch04-3-summary/src/01_e2e_research_agent.py

ui: ## 在浏览器打开 Gradio UI (http://localhost:7861)
	@echo "Gradio UI 在 http://localhost:7861"
	@echo "如果还没启动: make up"
	@which start && start http://localhost:7861 || \
	 which open && open http://localhost:7861 || \
	 which xdg-open && xdg-open http://localhost:7861 || \
	 echo "请手动浏览器打开 http://localhost:7861"

# ===== 环境检查 =====

check-env: ## 检查 .env 配置 + LLM 调用通畅
	docker compose run --rm app python scripts/check-env.py

doctor: ## Docker 环境诊断
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker Compose version:"
	@docker compose version
	@echo ""
	@echo "Disk usage:"
	@docker system df

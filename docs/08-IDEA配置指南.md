# IDEA / PyCharm 配置指南 — 像跑 Spring Boot 一样跑 Python

> 面向 **Java 工程师**: 你不用学 Docker 工作流, 也不用 `make shell` 进容器. 你只需要在 PyCharm 或 IntelliJ IDEA 里像跑 `Application.java` 一样**右键 Run** 任意 `01_xxx.py`. Docker 只负责跑两个中间件 (pgvector + redis), 跟你本地起 MySQL+Redis 一个意思.

本指南面向: **PyCharm Community / Professional 2024.1+** 或 **IntelliJ IDEA 2024.1+ (装 Python 插件)**.
所有截图占位用 `> 截图: xxx.png` 标记, 真截图后续补.

---

## 1. 总览 · IDEA-first 工作流

```
Step 1  Docker 起中间件 (5 秒)
        make mw-up        # pgvector :5432 / redis :6379

Step 2  PyCharm 配 venv + .env (一次性, 5 分钟)
        (1) 配 Python SDK (本仓库 .venv)
        (2) mark common/ + labs/ 为 Sources Root
        (3) 装 EnvFile 插件 + 改 Run Config 模板

Step 3  右键 Run 任意 lab 脚本
        labs/ch04-1-quickstart-ui/src/01_quickstart.py
        IDEA 自动加载 .env, 自动连 localhost:5432 pgvector
```

对比 Java 工程师的熟悉路径:

| Java/Spring 习惯 | Python/IDEA 等价 |
|---|---|
| `pom.xml` / `build.gradle` | `requirements.txt` / `pyproject.toml` |
| Project SDK = OpenJDK 17 | Project SDK = Python 3.11 (.venv) |
| Maven `dependencies` | `pip install -r requirements.txt` |
| `application.yml` | `.env` |
| IDEA 里右键 Run `Application.java` | IDEA 里右键 Run `01_xxx.py` |
| `docker-compose up mysql redis` | `make mw-up` (起 pgvector + redis) |
| `src/main/java` 标 Sources Root | `common/` + `labs/` 标 Sources Root |

---

## 2. 前置条件

| 工具 | 版本 | 备注 |
|---|---|---|
| Python | **3.10 / 3.11** (强烈推荐 3.11) | Win 装时勾 "Add to PATH". 3.14 有依赖兼容警告, 别用. |
| PyCharm 或 IntelliJ IDEA | **2024.1+** | Community 够用. IDEA 需装 Python 插件 (Settings → Plugins 搜 Python). |
| Docker Desktop | **24.0+** | 只用来跑中间件. |
| Git | 任意 | clone 仓库 |

验证:
```bash
python --version          # Python 3.11.x
docker --version          # >= 24.0
docker compose version    # v2 / v5
```

---

## 3. Step-by-step · 第一次配置

### 3.1 Clone + 配 .env

```bash
git clone git@github.com:hutiefang76/hello-my-deep_agents.git
cd hello-my-deep_agents
cp .env.example .env
```

编辑 `.env`, 至少填两行:
```
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=tongyi
```

> 申请 key: <https://bailian.console.aliyun.com> (新用户免费额度足够走完全程)

### 3.2 创建 venv + 装依赖 (命令行做一次)

**Windows (PowerShell 或 cmd):**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 装完后命令行敲 `python -c "import langchain, deepagents; print('ok')"` 看到 `ok` 即依赖装好.

### 3.3 在 PyCharm 里打开项目

`File → Open` → 选仓库根目录 (含 `pyproject.toml` 那一层).

> 截图: pycharm-open-project.png

### 3.4 配置 Python SDK (Interpreter)

PyCharm 里:
1. 按 **Ctrl+Alt+S** (macOS: **Cmd+,**) 打开 Settings
2. 左侧找 **Project: hello-my-deep-agents → Python Interpreter**
3. 右上 **Add Interpreter → Add Local Interpreter**
4. 左侧选 **Virtualenv Environment → Existing**
5. 在 **Interpreter** 框右边点 **...**, 浏览到:
   - **Windows**: `<repo>\.venv\Scripts\python.exe`
   - **macOS / Linux**: `<repo>/.venv/bin/python`
6. 点 **OK → Apply → OK**

> 截图: pycharm-sdk-config.png

> 在 IntelliJ IDEA (非 PyCharm) 里, 路径是 **File → Project Structure → SDKs → +** → 选上面的 python 可执行文件.
> 参考官方文档:
> - PyCharm: <https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html>
> - IntelliJ IDEA: <https://www.jetbrains.com/help/idea/configuring-python-sdk.html>

**验证 SDK 已识别**: 打开 PyCharm 底部 **Terminal** (Alt+F12), 看到 prompt 自动带 `(.venv)` 前缀即配置成功.

### 3.5 标记 Sources Root (避免 ImportError)

> 这一步 Java 工程师最容易忽略. 不标 Sources Root, 你 Run 脚本时会撞 `ModuleNotFoundError: No module named 'common'`.

操作:
1. 在 **Project** 工具窗口 (Alt+1) 找到 `common/` 文件夹
2. **右键 → Mark Directory as → Sources Root**, 文件夹图标变蓝色
3. 同样把 `labs/` 标为 **Sources Root**

> 截图: pycharm-mark-sources-root.png

或者用 Settings 一次性配:
- **Ctrl+Alt+S → Project: hello-my-deep-agents → Project Structure**
- 选 `common`, 点顶上的 **Sources** 按钮 (蓝色文件夹图标)
- 选 `labs`, 同样点 **Sources**
- **Apply → OK**

> 截图: pycharm-project-structure.png

参考官方文档:
- <https://www.jetbrains.com/help/pycharm/configuring-project-structure.html>
- <https://www.jetbrains.com/help/pycharm/content-root.html>

**验证**: 打开任意 `labs/ch04-*/src/*.py`, 顶上 `from common.llm import ...` 这行不再标红 = OK.

### 3.6 装 EnvFile 插件 (让 IDEA 自动加载 .env)

**为什么需要**: PyCharm 原生 Run Configuration 的 `Environment variables` 字段是手填的, 一行行复制 `.env` 累死. EnvFile 插件可以一键勾选某个 `.env` 文件, IDEA 启动脚本时自动注入所有变量, 等价于 Spring Boot 自动加载 `application.yml`.

**装插件**:
1. **Ctrl+Alt+S → Plugins → Marketplace**
2. 搜 **EnvFile** (作者: Borys Pierov / ashald)
3. **Install → Restart IDE**

> 截图: pycharm-envfile-plugin-install.png

**装好后的标志**: 打开任意 Run/Debug Configuration 编辑窗, 顶上 tab 出现 **EnvFile** 一栏.

参考插件主页: <https://github.com/ashald/EnvFile>

### 3.7 配 Python Run Configuration 模板 (一次性, 全局生效)

> 改 "模板" 而不是逐个 Run Configuration, 以后每次右键 Run 新脚本都自动继承.

操作:
1. 顶部菜单 **Run → Edit Configurations...**
2. 左侧最下面 **Edit configuration templates...**
3. 选 **Python** 模板
4. 配两件事:

   **(a) 工作目录 + PYTHONPATH** (右侧字段):
   - **Working directory**: 点右边 `...` → 选**仓库根目录** (含 `pyproject.toml` 那一层). 这等价于 Spring Boot 的 `user.dir = $PROJECT_DIR$`.
   - **Add content roots to PYTHONPATH** 已经被默认勾上, 保持默认即可.

   **(b) 启用 EnvFile** (顶部 EnvFile tab):
   - 勾 **Enable EnvFile**
   - 点 **+ → .env file** → 选仓库根 `.env`
   - 勾 **Substitute Environment Variables** (可选, 让占位符在 .env 内可解析)

5. **Apply → OK**

> 截图: pycharm-run-config-template.png
> 截图: pycharm-envfile-tab.png

---

## 4. 跑 Lab 的标准动作

### 4.1 起中间件

终端 (PyCharm 内嵌或外置都行):
```bash
make mw-up
```

或不用 make:
```bash
docker compose -f docker-compose.middleware.yml up -d
```

看到 `pgvector` + `redis` 两个容器 healthy 即 OK:
```bash
docker compose -f docker-compose.middleware.yml ps
```

### 4.2 IDEA 里 Run 脚本

打开任意 lab 脚本, 比如:
```
labs/ch04-1-quickstart-ui/src/01_quickstart.py
```

直接顶上点绿色三角 **Run**, 或右键 → **Run "01_quickstart"**.

> 截图: pycharm-run-script.png

第一次跑, IDEA 会基于上面配的模板自动生成一份 Run Configuration, 加载 `.env`, PYTHONPATH 包含 `common` 和 `labs`. 之后改代码再跑直接按 **Shift+F10**.

### 4.3 关中间件 (下班前)

```bash
make mw-down
```

数据卷保留, 下次 `mw-up` 上来记忆/向量数据还在.

---

## 5. 常见 lab 路径速查

| Lab | 入口脚本 | 是否需要中间件 |
|---|---|---|
| Ch1 Python 基础 | `labs/ch01-python-basics/src/01_hello_world.py` | 不需 |
| Ch2 LangChain 基础 | `labs/ch02-langchain-basics/src/01_llm_call.py` | 不需 |
| Ch3 三框架对比 | `labs/ch03-frameworks-compare/src/01_langchain.py` | 不需 |
| Ch4.1 Quickstart UI | `labs/ch04-1-quickstart-ui/src/01_quickstart.py` | 不需 |
| Ch4.2.1 多层记忆 | `labs/ch04-2-1-memory/src/03_long_term_pgvector.py` | 需 pgvector + redis |
| Ch4.2.3 Tools + RAG | `labs/ch04-2-3-tools-rag/src/02_pgvector_rag.py` | 需 pgvector |
| Ch4.3 集大成 demo | `labs/ch04-3-summary/src/01_e2e_research_agent.py` | 需 pgvector + redis |
| Ch9 L1-L5 演化 | `labs/ch09-cognitive-arch/src/06_evolution_compare.py` | 不需 |

需要中间件的 lab, 提前一句 `make mw-up` 即可.

---

## 6. 排错 (Troubleshooting)

> Java 工程师定位 Python 问题最常踩这五个坑. 按出现频率排序.

### 6.1 ModuleNotFoundError: No module named "common"

**根因**: `common/` 没标 Sources Root, 或 Run Configuration 的 PYTHONPATH 没含仓库根.

**修复**:
1. 检查 `common/` 在 Project 视图里图标是否蓝色 (Sources Root). 不是 → 右键 Mark Directory as → Sources Root.
2. **Run → Edit Configurations** → 当前 config → 确认 **Add content roots to PYTHONPATH** 已勾.
3. **Working directory** 填仓库根目录 (含 `pyproject.toml` 那一层), 不是 `labs/chxx/src/`.

### 6.2 KeyError DASHSCOPE_API_KEY 或 LLM 调用 401

**根因**: EnvFile 插件没装 / 没启用 / Run Configuration 没勾 EnvFile tab.

**修复**:
1. **Ctrl+Alt+S → Plugins → Installed**, 确认 **EnvFile** 已装且启用.
2. **Run → Edit Configurations** → 当前 config → **EnvFile** tab → 必须有一行勾上 `.env` 文件.
3. 如果是改了 Run Configuration **模板** 但已存在的旧 config 不生效: 删掉旧 config, 重新右键 Run 让 IDEA 基于新模板生成.
4. 临时验证: 在脚本最顶加 `import os; print("KEY=", os.getenv("DASHSCOPE_API_KEY"))`, Run 看是否打印出 `sk-xxx`.

### 6.3 psycopg.OperationalError 连不上 localhost:5432

**根因**: pgvector 没起, 或起在别的端口.

**修复**:
```bash
# 1. 看中间件状态
docker compose -f docker-compose.middleware.yml ps

# 2. 没起就起
make mw-up

# 3. 看日志, 确认 healthy
docker compose -f docker-compose.middleware.yml logs pgvector | tail -20
```

如果端口被占 (Win 里常见 5432 被本地 PostgreSQL 占), 编辑 `.env`:
```
PGVECTOR_PORT=5433
```
然后重启:
```bash
make mw-down && make mw-up
```

### 6.4 redis 连不上 localhost:6379

同上, 跑 `make mw-up` + 检查 `make mw-ps`. 端口冲突改 `.env` 里 `REDIS_PORT`.

### 6.5 PyCharm 解释器找不到 / SDK Invalid

**根因**: `.venv` 还没建, 或路径填错.

**修复**:
```bash
# 仓库根目录, 命令行重建 venv
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

然后回到 PyCharm Step 3.4 重选 `python.exe` / `python` 路径.

### 6.6 改了代码 IDE 飘红但运行正常 / 反之

**根因**: PyCharm 索引坏了.

**修复**: **File → Invalidate Caches → Invalidate and Restart**.

---

## 7. 进阶 · 调试 (Debug)

跟 IDEA 调 Java 一模一样:

1. 在脚本里点击代码行号左边, 留下红圆点 = 断点
2. 顶部按 **Debug** (绿色三角旁边那个), 或 **Shift+F9**
3. 程序运行到断点处自动暂停, 底部 **Debugger** 工具窗显示局部变量 / 调用栈
4. 常用快捷键: **F8 = step over, F7 = step into, Alt+F9 = run to cursor**

> 截图: pycharm-debug-breakpoint.png

调 LangChain Agent 的 tool calling 流时, 在 `common/llm.py` 的 `invoke()` 处下断点最直观.

---

## 8. FAQ

**Q1: 我没装 Docker 也能跑 lab 吗?**
A: 能, 只要这个 lab 不需要中间件 (上面 5 节表第三列写 "不需"). 即 Ch1-Ch4.1 / Ch9 / Ch5-Ch8 大部分都能直接跑. Ch4.2.1 (long-term memory) / Ch4.2.3 RAG / Ch4.3 e2e demo 必须 `make mw-up`.

**Q2: 我已经有装好的 Python 3.11 在系统里, 一定要建 .venv 吗?**
A: 强烈建议. 不然 `pip install -r requirements.txt` 会污染系统 Python. 这跟 Java 项目用 Maven local repo 隔离依赖一个道理.

**Q3: PyCharm Community 够吗?**
A: 够. Resource Roots 是 Pro 功能, 我们用不到. Sources Root 在 Community 也支持.

**Q4: 我用 VS Code 行不行?**
A: 行, 但本指南只覆盖 IDEA / PyCharm. VS Code 的等价配置: 装 Python 扩展 + Pylance, 选解释器 → `.venv/bin/python`, `.vscode/launch.json` 里 `envFile: ".env"`. 本仓库不维护 VS Code 配置.

**Q5: 跨平台 (Win / macOS) 路径分隔符怎么办?**
A: Python 代码内统一用 `pathlib.Path` 或 `os.path.join`, 别 hard code 反斜杠. 仓库现有代码已遵守这个约定.

---

## 9. 参考

- PyCharm 官方 · 配置 Python 解释器: <https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html>
- PyCharm 官方 · 项目结构 (Sources Root): <https://www.jetbrains.com/help/pycharm/configuring-project-structure.html>
- PyCharm 官方 · Content Root 详解: <https://www.jetbrains.com/help/pycharm/content-root.html>
- PyCharm 官方 · 创建 Virtualenv: <https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html>
- PyCharm 官方 · Run/Debug Configurations: <https://www.jetbrains.com/help/pycharm/run-debug-configuration.html>
- IntelliJ IDEA 官方 · 配置 Python SDK: <https://www.jetbrains.com/help/idea/configuring-python-sdk.html>
- EnvFile 插件主页: <https://github.com/ashald/EnvFile>
- 仓库 Docker 完整路径备选: [05-Docker部署指南.md](05-Docker部署指南.md)

---

> **核心心法**: Java 工程师转 Python, 最大障碍不是语法而是工作流. 把 IDEA-first 跑通你就过了 80% 的坎.

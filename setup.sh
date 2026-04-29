#!/usr/bin/env bash
# ============================================================
# hello-my-deep_agents · macOS/Linux 一键 setup (5 分钟搞定)
# ============================================================
# 做什么:
#   1. 在项目根建 .venv (Python 3.10+)
#   2. pip install -r requirements.txt
#   3. 校验关键模块 import
#
# 用法:
#   bash setup.sh
# ============================================================

set -euo pipefail
cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅${NC} $*"; }
warn() { echo -e "${YELLOW}⚠️${NC}  $*"; }
fail() { echo -e "${RED}❌${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}▶${NC} $*"; }

echo "============================================================"
echo "  hello-my-deep_agents — macOS/Linux setup"
echo "============================================================"

# Step 1: Python check
info "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    fail "python3 not found. Install Python 3.10+ from https://www.python.org/downloads/"
fi
PYVER=$(python3 --version | awk '{print $2}')
ok "Python $PYVER found"

# Step 2: 创建 .venv
info "[2/4] Creating .venv ..."
if [ -f ".venv/bin/python" ]; then
    ok ".venv already exists, skip create"
else
    python3 -m venv .venv || fail "venv create failed"
    ok ".venv created"
fi

# Step 3: 装依赖
info "[3/4] Installing dependencies (~3-5 minutes first time)..."
.venv/bin/python -m pip install --upgrade pip --quiet || fail "pip upgrade failed"
.venv/bin/python -m pip install -r requirements.txt || fail "pip install failed"
ok "root requirements installed"

if [ -f "labs/ch10-rag-multi-retrieval/requirements.txt" ]; then
    info "Installing Ch10 extras (rank_bm25 + jieba)..."
    .venv/bin/python -m pip install -r labs/ch10-rag-multi-retrieval/requirements.txt
fi

# Step 4: 校验关键模块
info "[4/4] Verifying critical imports..."
.venv/bin/python -c "import dotenv, langchain, langgraph, gradio, pydantic; print('   [OK] dotenv / langchain / langgraph / gradio / pydantic')" \
    || fail "import check failed"

# Check .env
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    warn "PLEASE EDIT .env and fill DASHSCOPE_API_KEY"
    warn "Apply key: https://bailian.console.aliyun.com/"
fi

echo ""
echo "============================================================"
ok "Setup complete!"
echo "============================================================"
echo ""
echo "  Next steps:"
echo "    1. Edit .env, fill DASHSCOPE_API_KEY"
echo "    2. (Optional) Start middleware: make mw-up"
echo "    3. Open PyCharm, Settings → Project → Python Interpreter"
echo "       → Add Local Interpreter → Existing → .venv/bin/python"
echo "    4. Right-click any labs/.../src/01_xxx.py → Run"
echo ""
echo "  Full guide: docs/08-PyCharm配置指南.md"
echo ""

#!/usr/bin/env bash
# verify.sh — Lab Ch02 LangChain 基础 一键验证
#
# 跑法: bash verify.sh
# 注意: 此 lab 会真实调用 DashScope API (qwen-plus), 大约消耗 30-50 个 API 请求

set -euo pipefail
cd "$(dirname "$0")"

export PYTHONIOENCODING=utf-8

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅${NC} $*"; }
fail() { echo -e "${RED}❌${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}▶${NC} $*"; }

echo "============================================================"
echo "Lab Ch02 · LangChain 基础 — verify.sh"
echo "============================================================"

# ===== 1. 环境 + 依赖 + LLM 调用通畅 =====
info "Step 1/2: 环境 + LLM 调用检查"
python ../../scripts/check-env.py || fail "环境/LLM 检查失败"

# ===== 2. 跑 5 个脚本, 每个都真调 LLM =====
echo
info "Step 2/2: 跑所有脚本 (真调 DashScope)"
for f in src/0[1-5]_*.py; do
    info "  → $f"
    python "$f" > /tmp/ch02_$(basename "$f" .py).log 2>&1 \
        && ok "    PASSED" \
        || { echo "--- log ---"; cat /tmp/ch02_$(basename "$f" .py).log; fail "$f 失败"; }
done

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch02 全部验证通过 ✅${NC}"
echo "============================================================"

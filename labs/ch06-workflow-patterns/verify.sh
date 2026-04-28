#!/usr/bin/env bash
# verify.sh — Lab Ch06 五大 Workflow Patterns 一键验证

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
echo "Lab Ch06 · 五大 Workflow Patterns — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑 4 个脚本 (各调多次 LLM)"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py; do
    info "  → $f"
    OUT=/tmp/ch06_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        grep -E "(Step [1-3]|Round|加速比|Voting|Sectioning|结构|Q[1-5])" "$OUT" 2>/dev/null | head -8 | sed 's/^/      /' || true
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch06 全部验证通过 ✅${NC}"
echo "============================================================"

#!/usr/bin/env bash
# verify.sh — Lab Ch05 Workflow vs Agent 一键验证

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
echo "Lab Ch05 · Workflow vs Agent — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑 3 个脚本"
for f in src/01_*.py src/02_*.py src/03_*.py; do
    info "  → $f"
    OUT=/tmp/ch05_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        grep -E "(推荐:|Reasoning|L[1-5]|Scenario|延迟比|成本比)" "$OUT" 2>/dev/null | head -8 | sed 's/^/      /' || true
    else
        echo "--- log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch05 全部验证通过 ✅${NC}"
echo "============================================================"

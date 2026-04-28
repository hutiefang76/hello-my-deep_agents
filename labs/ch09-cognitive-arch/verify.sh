#!/usr/bin/env bash
# verify.sh — Lab Ch09 Cognitive Architecture L1→L5 演化

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
echo "Lab Ch09 · Cognitive Architecture L1→L5 — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑 L1-L5 5 个脚本"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py src/05_*.py; do
    info "  → $f"
    OUT=/tmp/ch09_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        grep -E "(命中率|Q:|level|✅|❌|tools_used)" "$OUT" 2>/dev/null | head -6 | sed 's/^/      /' || true
    else
        echo "--- log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

info "Step 3: 演化对比 (06_evolution_compare.py)"
OUT=/tmp/ch09_06.log
if python src/06_evolution_compare.py > "$OUT" 2>&1; then
    ok "  06 evolution compare PASSED"
    grep -E "(L[1-5].*ms|Q:|演化总结|Chase)" "$OUT" 2>/dev/null | head -15 | sed 's/^/      /' || true
else
    echo "--- 06 log (last 30 lines) ---"
    tail -30 "$OUT"
    fail "06 失败"
fi

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch09 全部验证通过 ✅ — Course v3.0 Done! 🎉${NC}"
echo "============================================================"

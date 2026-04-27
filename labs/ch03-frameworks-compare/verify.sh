#!/usr/bin/env bash
# verify.sh — Lab Ch03 框架对比 一键验证
# 跑三个研究 Agent, 对比代码量 + 工具调用数 + 耗时

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
echo "Lab Ch03 · 框架对比 — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑三个研究 Agent (各约 30-60s)"

LOG=/tmp/ch03_metrics.log
> "$LOG"

for f in src/01_*.py src/02_*.py src/03_*.py; do
    info "  → $f"
    OUT=/tmp/ch03_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        # 抽 metrics 行
        grep ">>> METRICS" "$OUT" >> "$LOG" || true
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

echo
echo "============================================================"
echo "三框架对比 (从 stdout 抓的指标)"
echo "============================================================"
cat "$LOG"
echo

# 代码行数对比
echo "代码行数 (loc, 不含空行/注释):"
for f in src/01_*.py src/02_*.py src/03_*.py; do
    LOC=$(grep -cE "^[[:space:]]*[^#[:space:]]" "$f" || echo "?")
    printf "  %-30s %s 行\n" "$f" "$LOC"
done

echo
echo -e "${GREEN}Lab Ch03 全部验证通过 ✅${NC}"

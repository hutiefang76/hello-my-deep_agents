#!/usr/bin/env bash
# verify.sh — Lab Ch04.2.3 工具调用 + RAG 一键验证

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
echo "Lab Ch04.2.3 · 工具调用 + RAG — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 检查 docs 目录"
DOC_COUNT=$(ls docs/*.md 2>/dev/null | wc -l)
if [ "$DOC_COUNT" -lt 3 ]; then
    fail "docs/*.md 不足 3 个 (got $DOC_COUNT), RAG lab 需要至少 3 篇"
fi
ok "  docs/*.md = $DOC_COUNT 篇"

info "Step 3: 跑 3 个脚本"
for f in src/01_*.py src/02_*.py src/03_*.py; do
    info "  → $f"
    OUT=/tmp/ch423_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        grep -E "(\[Step|\[来源|\[指标|向量化|切分|加载)" "$OUT" 2>/dev/null | head -8 | sed 's/^/      /' || true
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch04.2.3 全部验证通过 ✅${NC}"
echo "============================================================"

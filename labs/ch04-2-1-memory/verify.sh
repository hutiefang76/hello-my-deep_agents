#!/usr/bin/env bash
# verify.sh — Lab Ch04.2.1 多层记忆 一键验证

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
echo "Lab Ch04.2.1 · 多层记忆 — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑 4 个脚本"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py; do
    info "  → $f"
    OUT=/tmp/ch421_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        # 抽指标
        grep -E "(消息总数|✅|⚠️|当前 messages 长度|向量库初始化|检索) " "$OUT" 2>/dev/null | head -8 | sed 's/^/      /' || true
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

# 清理临时 db (避免污染下次跑)
rm -f src/_memory.db src/_three_layer.db

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch04.2.1 全部验证通过 ✅${NC}"
echo "============================================================"

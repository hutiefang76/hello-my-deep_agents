#!/usr/bin/env bash
# verify.sh — Lab Ch10 RAG 多路召回 一键验证
#
# 跑完 = 7 个脚本全过 + 07 输出对比表

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
echo "Lab Ch10 · RAG 多路召回 — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 装 Ch10 增量依赖 (rank_bm25 + jieba)"
pip install -q -r requirements.txt 2>&1 | tail -3 || fail "pip install 失败"
python -c "import rank_bm25, jieba" || fail "rank_bm25 / jieba 不可用"
ok "  rank_bm25 + jieba 已就绪"

info "Step 3: 检查 docs 语料 (>=5 篇 .md, 总行数 >=200)"
DOC_COUNT=$(ls docs/*.md 2>/dev/null | wc -l)
TOTAL_LINES=$(cat docs/*.md 2>/dev/null | wc -l)
if [ "$DOC_COUNT" -lt 5 ]; then
    fail "docs/*.md 不足 5 篇 (got $DOC_COUNT)"
fi
if [ "$TOTAL_LINES" -lt 200 ]; then
    fail "docs 总行数 $TOTAL_LINES < 200, 语料不够"
fi
ok "  docs/*.md = $DOC_COUNT 篇, 共 $TOTAL_LINES 行"

info "Step 4: 语法检查 7 个脚本"
for f in src/0*.py; do
    python -c "import ast; ast.parse(open('$f', encoding='utf-8').read())" \
        || fail "$f 语法错"
done
ok "  src/0*.py 7 个脚本语法 OK"

info "Step 5: 跑 6 个单功能脚本 (01-06)"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py src/05_*.py src/06_*.py; do
    info "  → $f"
    OUT=/tmp/ch10_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        grep -E "(Hit@5|Top-1|平均延迟|hypo|Reranker|RRF|入库)" "$OUT" 2>/dev/null \
            | head -5 | sed 's/^/      /' || true
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

info "Step 6: 跑集大成 07_recall_compare.py (输出对比表)"
OUT=/tmp/ch10_recall_compare.log
if python src/07_recall_compare.py > "$OUT" 2>&1; then
    ok "    PASSED"
    echo "    --- 对比表 ---"
    grep -E "(配置|baseline|bm25|hybrid|multiquery|hyde|reranker|---|^\|)" "$OUT" \
        | head -25 | sed 's/^/    /'
else
    echo "--- 07 log (last 40 lines) ---"
    tail -40 "$OUT"
    fail "07_recall_compare.py 失败"
fi

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch10 全部验证通过 ✅${NC}"
echo "============================================================"

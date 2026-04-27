#!/usr/bin/env bash
# verify.sh — Lab Ch04.3 总结 端到端 demo 一键验证

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
echo "Lab Ch04.3 · 总结 + 端到端 demo — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑端到端 demo (CLI)"
OUT=/tmp/ch43_e2e.log
if python src/01_e2e_research_agent.py > "$OUT" 2>&1; then
    ok "  src/01_e2e_research_agent.py PASSED"
    grep -E "(意图|长期记忆|tools_used|files=|\\[终稿)" "$OUT" 2>/dev/null | head -10 | sed 's/^/      /' || true
else
    echo "--- log (last 30 lines) ---"
    tail -30 "$OUT"
    fail "端到端 demo 失败"
fi

info "Step 3: Gradio Full UI 启动 + 探活"
PORT=7862  # 用 7862 避免和 Ch4.1 的 7861 冲突
GRADIO_PORT=$PORT python src/02_gradio_full_ui.py > /tmp/ch43_gradio.log 2>&1 &
GRADIO_PID=$!

sleep 12

if curl -fsS "http://localhost:$PORT/" > /dev/null 2>&1; then
    ok "  Gradio Full UI 启动 PASSED (port $PORT)"
else
    cat /tmp/ch43_gradio.log
    kill -9 $GRADIO_PID 2>/dev/null || true
    fail "  Gradio Full UI 启动失败"
fi

kill $GRADIO_PID 2>/dev/null || true
wait $GRADIO_PID 2>/dev/null || true

# 清理
rm -f src/_e2e_memory.db

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch04.3 全部验证通过 ✅${NC}"
echo "Course Done! 🎉"
echo "============================================================"

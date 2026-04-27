#!/usr/bin/env bash
# verify.sh — Lab Ch04.1 Quickstart + Gradio UI 一键验证

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
echo "Lab Ch04.1 · Quickstart + Gradio UI — verify.sh"
echo "============================================================"

info "Step 1: 环境检查"
python ../../scripts/check-env.py || fail "环境检查失败"

info "Step 2: 跑 CLI 脚本 (01 + 02)"
for f in src/01_*.py src/02_*.py; do
    info "  → $f"
    OUT=/tmp/ch041_$(basename "$f" .py).log
    if python "$f" > "$OUT" 2>&1; then
        ok "    PASSED"
        # 抽几个关键指标行
        grep -E "(消息总数|工具调用|用到的工具|虚拟 FS)" "$OUT" | head -10 | sed 's/^/      /'
    else
        echo "--- $f log (last 30 lines) ---"
        tail -30 "$OUT"
        fail "$f 失败"
    fi
done

info "Step 3: Gradio UI 启动 + 探活"
PORT=7861   # 用 7861 避免和真实开发的 7860 冲突
GRADIO_PORT=$PORT python src/03_gradio_ui.py > /tmp/ch041_gradio.log 2>&1 &
GRADIO_PID=$!

# 给它 8 秒启动 (Gradio 启动比 FastAPI 慢)
sleep 8

if curl -fsS "http://localhost:$PORT/" > /dev/null 2>&1; then
    ok "  Gradio UI 启动 PASSED (port $PORT)"
else
    cat /tmp/ch041_gradio.log
    kill -9 $GRADIO_PID 2>/dev/null || true
    fail "  Gradio UI 启动失败"
fi

# 关掉
kill $GRADIO_PID 2>/dev/null || true
wait $GRADIO_PID 2>/dev/null || true

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch04.1 全部验证通过 ✅${NC}"
echo "============================================================"

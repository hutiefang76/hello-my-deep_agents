#!/usr/bin/env bash
# verify.sh — Lab Ch01 Python 基础 一键验证
#
# 跑法: bash verify.sh
# 退出码: 0 全绿, 非 0 有错

set -euo pipefail

cd "$(dirname "$0")"

# Windows GBK 终端兜底: 让 stdout 走 UTF-8, 防止中文/emoji 触发 UnicodeEncodeError
export PYTHONIOENCODING=utf-8

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅${NC} $*"; }
fail() { echo -e "${RED}❌${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}▶${NC} $*"; }

echo "============================================================"
echo "Lab Ch01 · Python 基础 — verify.sh"
echo "============================================================"

# ===== 1. 语法检查所有脚本 =====
info "Step 1/3: 语法检查 (py_compile)"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py src/05_*.py src/06_*.py src/_demo_package/*.py; do
    python -m py_compile "$f" || fail "$f 语法错"
    ok "  $f"
done
# 07 是 web server, 单独 syntax check (不能直接跑会阻塞)
python -m py_compile src/07_fastapi_mini.py || fail "src/07_fastapi_mini.py 语法错"
ok "  src/07_fastapi_mini.py"

# ===== 2. 跑无 web server 的脚本 (应该都能 0 秒退出) =====
echo
info "Step 2/3: 跑非 web 脚本 (应该都能秒退)"
for f in src/01_*.py src/02_*.py src/03_*.py src/04_*.py src/05_*.py src/06_*.py; do
    python "$f" > /dev/null 2>&1 || fail "$f 运行失败"
    ok "  $f PASSED"
done

# ===== 3. FastAPI 启动后探活 (依赖装好才跑, 否则 skip) =====
echo
info "Step 3/3: FastAPI 启动 + 探活 (需要 pip install fastapi uvicorn)"

if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}  ⊘ 跳过${NC} — fastapi/uvicorn 未安装"
    echo "    请先 cd ../.. && pip install -r requirements.txt"
else
    python src/07_fastapi_mini.py > /tmp/ch01_fastapi.log 2>&1 &
    FASTAPI_PID=$!

    # 给它 3 秒启动
    sleep 3

    # 探活
    if curl -fsS http://localhost:8000/health > /dev/null 2>&1; then
        ok "  FastAPI /health PASSED"
    else
        cat /tmp/ch01_fastapi.log
        kill -9 $FASTAPI_PID 2>/dev/null || true
        fail "  FastAPI 启动失败"
    fi

    # 关掉
    kill $FASTAPI_PID 2>/dev/null || true
    wait $FASTAPI_PID 2>/dev/null || true
fi

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch01 全部验证通过 ✅${NC}"
echo "============================================================"

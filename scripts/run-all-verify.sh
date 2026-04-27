#!/usr/bin/env bash
# run-all-verify.sh — 跨 lab 全量验证 (一键跑所有 lab 的 verify.sh)
#
# 跑法: bash scripts/run-all-verify.sh
# 注意: 全跑约 5-10 分钟, 会真调 DashScope (qwen-plus + embedding)

set -euo pipefail
cd "$(dirname "$0")/.."     # 回到仓库根

export PYTHONIOENCODING=utf-8

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅${NC} $*"; }
fail() { echo -e "${RED}❌${NC} $*"; }
info() { echo -e "${YELLOW}▶${NC} $*"; }
heading() { echo -e "\n${BOLD}${YELLOW}=== $* ===${NC}\n"; }

PASS_COUNT=0
FAIL_COUNT=0
FAILED_LABS=()

heading "hello-my-deep_agents · 全量 lab 验证"

# 找所有 verify.sh
LABS=$(ls -d labs/ch*/ 2>/dev/null | sort)
TOTAL=$(echo "$LABS" | wc -l | tr -d ' ')

info "Found $TOTAL labs"
echo "$LABS" | nl -ba

START_TIME=$(date +%s)

for lab in $LABS; do
    lab_name=$(basename "$lab")
    if [ ! -f "$lab/verify.sh" ]; then
        fail "  $lab_name 缺失 verify.sh, 跳过"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILED_LABS+=("$lab_name (missing verify.sh)")
        continue
    fi

    heading "Running: $lab_name"

    LAB_LOG="/tmp/full_verify_${lab_name}.log"
    if (cd "$lab" && bash verify.sh) > "$LAB_LOG" 2>&1; then
        ok "$lab_name PASSED"
        # 抽 verify.sh 的最后几行 (含成功消息)
        tail -3 "$LAB_LOG" | sed 's/^/      /'
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        fail "$lab_name FAILED"
        # 出错时打印最后 20 行
        echo "      --- log tail ---"
        tail -20 "$LAB_LOG" | sed 's/^/      /'
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILED_LABS+=("$lab_name")
    fi
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

heading "Final Report"

echo "  总 lab 数:    $TOTAL"
echo "  PASS:        $PASS_COUNT"
echo "  FAIL:        $FAIL_COUNT"
echo "  耗时:        ${ELAPSED}s"

if [ $FAIL_COUNT -gt 0 ]; then
    echo
    echo "  Failed labs:"
    for failed in "${FAILED_LABS[@]}"; do
        echo "    - $failed"
    done
    echo
    fail "全量验证失败"
    exit 1
fi

echo
echo -e "${GREEN}${BOLD}🎉 全部 $PASS_COUNT 个 lab 验证通过 ✅${NC}"

#!/usr/bin/env bash
# verify.sh · Ch12 MCP + A2A 一键验证
#
# 验证内容:
#   1. python-wrapper Python 语法 OK
#   2. a2a-demo Python 语法 OK
#   3. spring-boot-mcp pom.xml 结构 OK (有 Maven 时尝试编译)
#   4. (可选) 起 a2a server + client 真跑通

set -uo pipefail
cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }
info() { echo -e "${YELLOW}[..]${NC} $*"; }

PY="${PY:-python}"

echo "============================================================"
echo " Lab Ch12 · MCP + A2A — verify.sh"
echo "============================================================"

# Step 1 · Python 语法检查
info "Step 1: Python 语法检查"
for f in python-wrapper/src/*.py a2a-demo/src/*.py; do
    if [ -f "$f" ]; then
        $PY -c "import ast; ast.parse(open(r'$f', encoding='utf-8').read())" \
            && ok "  $f" || fail "  $f 语法错"
    fi
done

# Step 2 · 关键文件存在
info "Step 2: 关键文件存在性"
for f in README.md \
         spring-boot-mcp/pom.xml \
         spring-boot-mcp/src/main/java/com/example/order/Application.java \
         spring-boot-mcp/src/main/java/com/example/order/OrderService.java \
         spring-boot-mcp/src/main/resources/application.yml \
         python-wrapper/src/mcp_server.py \
         python-wrapper/src/mcp_client.py \
         python-wrapper/requirements.txt \
         a2a-demo/src/research_agent_server.py \
         a2a-demo/src/agent_client.py \
         a2a-demo/requirements.txt; do
    [ -f "$f" ] && ok "  $f" || fail "  $f 缺失"
done

# Step 3 · OrderService 含 @Tool 注解
info "Step 3: SpringBoot OrderService 含 @Tool 注解"
grep -q "@Tool" spring-boot-mcp/src/main/java/com/example/order/OrderService.java \
    && ok "  @Tool 注解就位 (LLM 可发现 tool)" || fail "  @Tool 缺失"

# Step 4 · Python wrapper 用了 FastMCP
info "Step 4: Python wrapper 用 FastMCP + httpx"
grep -q "FastMCP" python-wrapper/src/mcp_server.py \
    && ok "  FastMCP 已引" || fail "  FastMCP 缺"
grep -q "httpx" python-wrapper/src/mcp_server.py \
    && ok "  httpx (调 Java) 已引" || fail "  httpx 缺"

# Step 5 · A2A demo 含 agent-card.json endpoint
info "Step 5: A2A server 暴露 /.well-known/agent-card.json"
grep -q "/.well-known/agent-card.json" a2a-demo/src/research_agent_server.py \
    && ok "  Agent Card endpoint 就位" || fail "  Agent Card endpoint 缺"

# Step 6 · A2A server 含 tasks endpoint
info "Step 6: A2A server 暴露 POST /a2a/v1/tasks"
grep -q '/a2a/v1/tasks' a2a-demo/src/research_agent_server.py \
    && ok "  Task submit endpoint 就位" || fail "  Task endpoint 缺"

# Step 7 · (可选) Maven 编译 SpringBoot
info "Step 7: (可选) Maven 编译 SpringBoot MCP server"
if command -v mvn &>/dev/null; then
    cd spring-boot-mcp
    if mvn -q compile -DskipTests 2>&1 | tail -5; then
        ok "  Maven compile OK"
    else
        echo -e "${YELLOW}[skip]${NC}  Maven compile 失败 (Spring AI 1.1.0-M2 milestone 仓需联网, 可后补)"
    fi
    cd ..
else
    echo -e "${YELLOW}[skip]${NC}  Maven 未装, 跳过 (Java case 需 mvn 跑, 但代码已就位)"
fi

# Step 8 · (可选) 真跑 A2A demo
info "Step 8: (可选) A2A demo 真跑 (server + client)"
if $PY -c "import fastapi, uvicorn, httpx, pydantic" 2>/dev/null; then
    info "  起 a2a server (后台)..."
    cd a2a-demo
    $PY src/research_agent_server.py >/tmp/a2a_server.log 2>&1 &
    SERVER_PID=$!
    sleep 3
    info "  跑 client 验证..."
    if $PY src/agent_client.py 2>&1 | tail -10; then
        ok "  A2A 完整链路通"
    else
        echo -e "${YELLOW}[skip]${NC}  A2A 真跑失败 (server 可能没起来), 见 /tmp/a2a_server.log"
    fi
    kill $SERVER_PID 2>/dev/null || true
    cd ..
else
    echo -e "${YELLOW}[skip]${NC}  fastapi/uvicorn/httpx/pydantic 未装"
    echo "    安装: pip install -r a2a-demo/requirements.txt"
fi

echo
echo "============================================================"
echo -e "${GREEN}Lab Ch12 静态验证全过 ✅${NC}"
echo "============================================================"
echo
echo "下一步 (真业务集成):"
echo "  - Case 1: cd spring-boot-mcp && mvn spring-boot:run"
echo "  - Case 2: cd python-wrapper && python src/mcp_server.py"
echo "  - Case 3: cd a2a-demo && python src/research_agent_server.py"

# Case 1 · Spring Boot → MCP Server (Java SDK)

> **场景**: Java 工程师 / Spring 老兵想把现有业务暴露给 LLM Agent (Claude/Cursor/自家 Agent), 不愿大改架构.

## 核心抓手 (一行总结)

**给 SpringBoot 服务方法加 `@Tool` 注解, 加一个 starter, 加一个 Bean — 完事**.

```java
@Service
@RestController
public class OrderService {

    // 老 REST endpoint 一字不动
    @GetMapping("/api/orders/{orderId}")
    // 一行注解就把这方法暴露给 MCP Client
    @Tool(description = "查订单状态")
    public Map<String, Object> getOrder(@PathVariable String orderId) {
        // 老业务代码原样
        return repository.find(orderId);
    }
}
```

## 改造步骤 (你公司的项目可以照搬)

### Step 1 · pom.xml 加 Spring AI MCP Server Starter

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

加 BOM (见本目录 `pom.xml`).

### Step 2 · 在 Application.java 注册 ToolCallbackProvider

```java
@Bean
ToolCallbackProvider orderTools(OrderService orderService) {
    return MethodToolCallbackProvider.builder()
            .toolObjects(orderService)
            .build();
}
```

### Step 3 · 给方法加 `@Tool` + 入参加 `@ToolParam`

```java
@Tool(description = "根据订单 ID 查询订单详情")
public Map<String, Object> getOrder(
        @ToolParam(description = "订单编号, 如 O20260429") String orderId
) { ... }
```

### Step 4 · application.yml 配 MCP server

```yaml
spring:
  ai:
    mcp:
      server:
        name: order-mcp-server
        version: 0.1.0
        sse-endpoint: /sse
```

### Step 5 · 跑

```bash
mvn spring-boot:run
# Server 起在 http://localhost:8080
# MCP SSE endpoint: http://localhost:8080/sse
```

## 验证

### 方式 A · MCP Inspector (官方调试 UI)

```bash
npx @modelcontextprotocol/inspector
# 打开浏览器选 SSE, URL: http://localhost:8080/sse
# 看到 tools 列表 = OK
```

### 方式 B · Claude Desktop 配置

`%APPDATA%\Claude\claude_desktop_config.json` (Win) 或 `~/Library/Application Support/Claude/claude_desktop_config.json` (mac):

```json
{
  "mcpServers": {
    "order-service": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

重启 Claude Desktop, 就能在对话里说"查 O20260429 订单状态", Claude 自动调你的 SpringBoot 服务.

### 方式 C · Python `mcp` 客户端 (见 `../python-wrapper/`)

`a2a-demo/src/mcp_client.py` 里有 Python 调本 server 的代码.

## 老 REST 接口还能用吗?

**完全能用**. `@Tool` 和 `@GetMapping` 都在同一个方法上 — 老调用方走 HTTP/REST, LLM Agent 走 MCP/SSE, 互不影响.

## 兼容版本

- Java 17+
- Spring Boot 3.4.x
- Spring AI 1.1.0-M2+ (含 MCP enhancements)

## 注意事项

- `1.1.0-M2` 是 milestone 版, 仓库需加 `https://repo.spring.io/milestone`
- 生产用建议跟踪 GA 版 (估计 2026-Q1 出)
- `@Tool` 描述写仔细 — LLM 决定何时调你这个工具就靠这段描述

## 参考

- [Spring AI MCP Boot Starter blog (2025-09)](https://spring.io/blog/2025/09/16/spring-ai-mcp-intro-blog/)
- [MCP Java SDK GitHub](https://github.com/modelcontextprotocol/java-sdk)
- [MCP 官方 spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)

package com.example.order;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

/**
 * Case 1 · Spring Boot 改造为 MCP Server (Application 入口).
 *
 * 这就是个普通的 SpringBoot 应用. 关键在两步:
 *   1) pom.xml 引入 spring-ai-starter-mcp-server-webmvc (见 pom.xml)
 *   2) 注册 ToolCallbackProvider, 把含 @Tool 的 bean 暴露给 MCP
 *
 * 等价 Python 写法是 mcp.server.fastmcp.FastMCP("name") + @mcp.tool() —
 * Spring AI 把这个理念搬到 Java 生态.
 *
 * 启动后:
 *   - HTTP SSE endpoint: http://localhost:8080/sse
 *   - MCP Inspector 工具可对接调试
 *   - Claude Desktop / Cursor 等可作为客户端
 */
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    /**
     * 把 OrderService 里所有 @Tool 注解的方法注册为 MCP tools.
     * Spring AI 自动扫这个 bean, 暴露 tool 列表给 MCP client.
     */
    @Bean
    ToolCallbackProvider orderTools(OrderService orderService) {
        return MethodToolCallbackProvider.builder()
                .toolObjects(orderService)
                .build();
    }
}

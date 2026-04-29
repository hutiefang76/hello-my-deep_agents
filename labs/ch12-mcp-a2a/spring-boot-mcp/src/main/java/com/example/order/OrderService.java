package com.example.order;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Case 1 · 订单服务 — 同一个 Service 既是 REST Controller, 又是 MCP Tool 提供者.
 *
 * 这是关键设计点: @Tool 是 Spring AI 的注解, 不影响原有 @RestController, 即:
 *   - 老的 HTTP 客户端 (浏览器/Postman/Java 同事) 照样调 GET /api/orders/O123
 *   - 新的 LLM Agent 通过 MCP 协议自动发现并调用这个 tool
 *   - 业务代码 0 改动, 只是多了一行 @Tool 注解
 *
 * 这就是用户问的 "把现有 SpringBoot 程序改成 MCP" 的核心抓手.
 */
@Service
@RestController
public class OrderService {

    // 模拟订单 DB — 真业务里这里是 JpaRepository / Mybatis Mapper
    private static final Map<String, Map<String, Object>> ORDERS = Map.of(
            "O20260429", Map.of("id", "O20260429", "status", "已发货", "total", 299.00, "items", 3),
            "O20260428", Map.of("id", "O20260428", "status", "已签收", "total", 89.00, "items", 1),
            "O20260427", Map.of("id", "O20260427", "status", "处理中", "total", 1599.00, "items", 5)
    );

    // ===== 既是 REST endpoint, 又是 MCP tool =====

    @GetMapping("/api/orders/{orderId}")
    @Tool(description = "根据订单 ID 查询订单详情. 入参: orderId (如 O20260429). 返回订单状态/金额/件数.")
    public Map<String, Object> getOrder(
            @PathVariable
            @ToolParam(description = "订单编号, 如 O20260429") String orderId
    ) {
        return ORDERS.getOrDefault(orderId, Map.of(
                "id", orderId,
                "status", "未找到",
                "error", "订单不存在"
        ));
    }

    @GetMapping("/api/orders")
    @Tool(description = "列出最近的订单. 用于 LLM 概览展示.")
    public List<Map<String, Object>> listOrders() {
        return List.copyOf(ORDERS.values());
    }

    @GetMapping("/api/orders/{orderId}/cancel")
    @Tool(description = "取消订单. 注意: 已发货订单无法取消, 会返回错误.")
    public Map<String, Object> cancelOrder(
            @PathVariable
            @ToolParam(description = "要取消的订单 ID") String orderId
    ) {
        var order = ORDERS.get(orderId);
        if (order == null) {
            return Map.of("error", "订单不存在: " + orderId);
        }
        var status = (String) order.get("status");
        if ("已发货".equals(status) || "已签收".equals(status)) {
            return Map.of("error", "已发货/已签收订单不允许取消", "current_status", status);
        }
        return Map.of("ok", true, "message", "订单 " + orderId + " 已取消");
    }
}

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.regex.Pattern;

/**
 * 等价 Python: src/07_fastapi_mini.py — 看这个文件感受 JDK 23 在做和 Python 同样的事.
 *
 * <p>核心对照:
 * <pre>
 *   Python FastAPI                     Spring Boot                       本文件 (纯 JDK)
 *   --------------                     -----------                       ---------------
 *   app = FastAPI()                    &amp;#64;SpringBootApplication        HttpServer.create
 *   &amp;#64;app.get("/x")                  &amp;#64;GetMapping("/x")                server.createContext
 *   Pydantic 自动校验                    &amp;#64;Valid + JSR-303                 手动 if + throw
 *   uvicorn (ASGI)                     Tomcat / Netty                    com.sun.net.httpserver
 *   /docs (auto Swagger)               springdoc-openapi                  无
 * </pre>
 *
 * <p>本文件不引外部依赖, 用 JDK 自带的 com.sun.net.httpserver 做最简 demo.
 * 真实项目用 Spring Boot 或 Javalin/Helidon/Quarkus.
 *
 * <p>JDK 23 特性使用:
 * <ul>
 *   <li>record — 数据模型 (等价 Pydantic BaseModel)</li>
 *   <li>text block — 多行 JSON 字符串</li>
 *   <li>switch expression — 路由分发</li>
 *   <li>Virtual Threads — server.setExecutor 用 vthread executor (JDK 21+)</li>
 *   <li>var 局部类型推断</li>
 * </ul>
 *
 * <p>对照 Spring Boot 等价代码 (要加 spring-boot-starter-web 依赖):
 * <pre>
 * &amp;#64;RestController
 * public class UserController {
 *   private final Map&lt;String, UserResponse&gt; users = new ConcurrentHashMap&lt;&gt;();
 *   &amp;#64;PostMapping("/users")
 *   public UserResponse create(&amp;#64;Valid &amp;#64;RequestBody UserCreate p) {
 *     var id = "u" + (users.size() + 1);
 *     var u = new UserResponse(id, p.name(), p.age(), p.email(), Instant.now());
 *     users.put(id, u);
 *     return u;
 *   }
 * }
 * </pre>
 */
class FastApiMini {

    /** 请求体 — 等价 Pydantic UserCreate (record 自动生成 ctor/accessor/equals). */
    record UserCreate(String name, int age, String email) {

        /** Compact ctor 校验 — 等价 Pydantic Field(min_length=1, ge=0). */
        public UserCreate {
            if (name == null || name.isBlank() || name.length() > 64) {
                throw new IllegalArgumentException("name 必须 1-64 字符");
            }
            if (age < 0 || age > 200) {
                throw new IllegalArgumentException("age 必须 0-200");
            }
        }
    }

    /** 响应体 — 等价 Pydantic UserResponse. */
    record UserResponse(String id, String name, int age, String email, Instant createdAt) {}

    /** 内存数据库 (教学用, 真实项目接 PG/Mongo). */
    private static final Map<String, UserResponse> USERS = new ConcurrentHashMap<>();

    public static void main(final String[] args) throws IOException {
        final var port = 8000;
        final var server = HttpServer.create(new InetSocketAddress(port), 0);
        // 路由注册 — 等价 FastAPI 的 @app.get/post
        server.createContext("/", FastApiMini::handleRoot);
        server.createContext("/health", FastApiMini::handleHealth);
        server.createContext("/users", FastApiMini::handleUsers);
        // JDK 21+ Virtual Thread executor — 等价 FastAPI 的 async + uvicorn
        // 每个请求一个 vthread, 一台机器轻松扛百万并发连接
        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());

        final var banner = """
                ============================================================
                FastAPI mini API 启动 (Java 等价版本)
                ============================================================
                  首页:        http://localhost:%d/
                  健康检查:     http://localhost:%d/health
                  用户列表:     http://localhost:%d/users
                  注: JDK HttpServer 不自带 Swagger, 真实项目用 Spring Boot
                ============================================================
                Ctrl+C 停止
                """.formatted(port, port, port);
        System.out.println(banner);
        server.start();
    }

    /** GET / — 首页. */
    static void handleRoot(final HttpExchange ex) throws IOException {
        final var body = """
                {
                  "message": "Hello FastAPI (Java equivalent)",
                  "users_count": "%d"
                }
                """.formatted(USERS.size());
        sendJson(ex, 200, body);
    }

    /** GET /health — 健康检查. */
    static void handleHealth(final HttpExchange ex) throws IOException {
        sendJson(ex, 200, """
                {"status": "ok"}
                """);
    }

    /** /users — switch expression 分发 (JDK 14+ stable). */
    static void handleUsers(final HttpExchange ex) throws IOException {
        final var method = ex.getRequestMethod();
        switch (method) {
            case "GET" -> handleListOrGet(ex);
            case "POST" -> handleCreate(ex);
            case "DELETE" -> handleDelete(ex);
            default -> sendJson(ex, 405, """
                    {"error": "method not allowed"}
                    """);
        }
    }

    static void handleListOrGet(final HttpExchange ex) throws IOException {
        final var path = ex.getRequestURI().getPath();
        if (path.equals("/users") || path.equals("/users/")) {
            sendJson(ex, 200, """
                    {"count": %d, "note": "demo 不序列化 list, 详见 Spring Boot 注释"}
                    """.formatted(USERS.size()));
            return;
        }
        final var id = path.substring("/users/".length());
        final var user = USERS.get(id);
        if (user == null) {
            sendJson(ex, 404, """
                    {"detail": "user not found"}
                    """);
        } else {
            sendJson(ex, 200, userToJson(user));
        }
    }

    /** POST /users — 创建用户. 极简 JSON 解析 (真实项目用 Jackson). */
    static void handleCreate(final HttpExchange ex) throws IOException {
        final var body = new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        try {
            final var payload = parseUserCreate(body);
            final var id = "u" + UUID.randomUUID().toString().substring(0, 8);
            final var user = new UserResponse(id, payload.name(), payload.age(),
                    payload.email(), Instant.now());
            USERS.put(id, user);
            sendJson(ex, 201, userToJson(user));
        } catch (IllegalArgumentException e) {
            sendJson(ex, 422, """
                    {"detail": "%s"}
                    """.formatted(e.getMessage()));
        }
    }

    /** DELETE /users/{id}. */
    static void handleDelete(final HttpExchange ex) throws IOException {
        final var path = ex.getRequestURI().getPath();
        final var id = path.substring("/users/".length());
        if (USERS.remove(id) == null) {
            sendJson(ex, 404, """
                    {"detail": "not found"}
                    """);
        } else {
            ex.sendResponseHeaders(204, -1);
            ex.close();
        }
    }

    /** 极简 JSON 解析 (教学用, 真实用 Jackson/Gson). */
    static UserCreate parseUserCreate(final String json) {
        final var name = extract(json, "name");
        final var ageStr = extract(json, "age");
        final var email = extract(json, "email");
        if (name == null) {
            throw new IllegalArgumentException("missing field: name");
        }
        return new UserCreate(name, ageStr == null ? 0 : Integer.parseInt(ageStr), email);
    }

    static String extract(final String json, final String key) {
        // 匹配 "key": "value" 或 "key": 123
        final var p = Pattern.compile(
                "\"" + key + "\"\\s*:\\s*(\"([^\"]*)\"|(-?\\d+))");
        final var m = p.matcher(json);
        if (m.find()) {
            return m.group(2) != null ? m.group(2) : m.group(3);
        }
        return null;
    }

    static String userToJson(final UserResponse u) {
        return """
                {
                  "id": "%s",
                  "name": "%s",
                  "age": %d,
                  "email": %s,
                  "created_at": "%s"
                }
                """.formatted(u.id(), u.name(), u.age(),
                u.email() == null ? "null" : "\"" + u.email() + "\"",
                u.createdAt());
    }

    static void sendJson(final HttpExchange ex, final int status, final String body) throws IOException {
        final var bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(bytes);
        }
    }
}

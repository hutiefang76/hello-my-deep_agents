"""07 · FastAPI mini — Python 的 Spring Boot.

对照:
    Spring Boot                              FastAPI
    ────────                                 ────────
    @SpringBootApplication                   app = FastAPI()
    @RestController                          @app.get/post/...
    @GetMapping("/users")                    @app.get("/users")
    @RequestBody UserDTO                     def x(payload: UserDTO):
    @ResponseBody                            (默认就是 JSON)
    @Valid + JSR-303                         Pydantic 校验自动跑
    Spring WebFlux Mono/Flux                 async def + StreamingResponse
    Swagger UI                               (默认自动生成 /docs)
    ApplicationRunner                        startup event / lifespan

Run:
    python 07_fastapi_mini.py
    # 然后浏览器打开:
    #   http://localhost:8000/        — 首页
    #   http://localhost:8000/docs    — 自动 Swagger
    #   http://localhost:8000/redoc   — ReDoc 文档
"""

from __future__ import annotations

from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

# ===== 1. 启动 app — 类似 Spring Boot 的 SpringApplication.run() =====
app = FastAPI(
    title="hello-my-deep_agents · Ch1 mini API",
    description="Python FastAPI 入门 demo, 对照 Spring Boot @RestController.",
    version="0.1.0",
)

# ===== 2. 数据模型 — 等同 Java POJO + JSR-303 校验 =====
class UserCreate(BaseModel):
    """请求体 — Pydantic 模型."""

    name: str = Field(..., min_length=1, max_length=64, description="用户名")
    age: int = Field(..., ge=0, le=200, description="年龄")
    email: str | None = Field(None, description="邮箱, 可选")


class UserResponse(BaseModel):
    """响应体."""

    id: str
    name: str
    age: int
    email: str | None
    created_at: datetime


# 内存数据库 (教学用 — 真实项目接 PG/Mongo)
_users: dict[str, UserResponse] = {}


# ===== 3. 路由 — 装饰器风格, 比 @GetMapping 更紧凑 =====
@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    """首页."""
    return {
        "message": "Hello FastAPI",
        "docs": "/docs",
        "users_count": str(len(_users)),
    }


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    tags=["users"],
)
async def create_user(payload: UserCreate) -> UserResponse:
    """新建用户 — 自动 Pydantic 校验, 失败返回 422."""
    user_id = f"u{len(_users) + 1}"
    user = UserResponse(
        id=user_id,
        name=payload.name,
        age=payload.age,
        email=payload.email,
        created_at=datetime.now(),
    )
    _users[user_id] = user
    return user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user(user_id: str = Path(..., description="用户 ID")) -> UserResponse:
    """按 ID 获取用户."""
    if user_id not in _users:
        raise HTTPException(status_code=404, detail=f"user '{user_id}' not found")
    return _users[user_id]


@app.get("/users", response_model=list[UserResponse], tags=["users"])
async def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[UserResponse]:
    """列出用户, 带分页参数 — Query 自动校验."""
    items = list(_users.values())
    return items[offset : offset + limit]


@app.delete("/users/{user_id}", status_code=204, tags=["users"])
async def delete_user(user_id: str) -> None:
    """删除用户."""
    if user_id not in _users:
        raise HTTPException(status_code=404, detail=f"user '{user_id}' not found")
    del _users[user_id]


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """健康检查 — 类似 Spring Boot Actuator /actuator/health."""
    return {"status": "ok"}


# ===== 4. 启动入口 =====
def main() -> None:
    """启动服务器 — uvicorn 是 Python 的 Tomcat (异步 ASGI 服务器)."""
    print("=" * 60)
    print("FastAPI mini API 启动")
    print("=" * 60)
    print("  首页:        http://localhost:8000/")
    print("  Swagger UI:  http://localhost:8000/docs")
    print("  ReDoc:       http://localhost:8000/redoc")
    print("=" * 60)
    print("Ctrl+C 停止")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()

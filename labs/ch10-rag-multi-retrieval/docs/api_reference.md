# API 参考手册

> 本手册列出后端核心 HTTP API. 用于 RAG 多路召回测试 — 这种"代号/型号/接口名"密集型文档最能体现 BM25 关键词召回相对向量召回的优势.

## 用户接口 /api/v1/users

### POST /api/v1/users/register
注册新用户. 请求体 JSON:
- username (string, 必填, 3-32 字符)
- email (string, 必填, RFC5322 格式)
- password (string, 必填, 至少 8 位含大小写数字)
- invite_code (string, 选填, 邀请码 INV-XXXX 格式)

返回 201, 体: `{user_id, access_token, refresh_token}`. 错误码 E1001 用户名已存在 / E1002 邮箱格式错 / E1003 密码强度不足.

### POST /api/v1/users/login
登录, 支持密码 + 短信验证码. 返回 access_token (有效期 2h) + refresh_token (有效期 30d). 错误码 E1101 账号密码错 / E1102 账号锁定 (5 次失败后锁 30 分钟) / E1103 二次验证未通过.

### GET /api/v1/users/me
获取当前用户. 需带 Authorization: Bearer <access_token>. 返回 `{user_id, username, email, vip_level, created_at}`.

## 订单接口 /api/v1/orders

### POST /api/v1/orders
创建订单. 字段: items (array of `{sku_id, quantity}`), shipping_address (object), payment_method (alipay/wechat/unionpay). 返回订单号 O20260427XXXXX.

### GET /api/v1/orders/{order_id}
查订单详情. 字段含: status (枚举 CREATED/PAID/SHIPPED/DELIVERED/CANCELLED), items, total_amount, courier_no.

### POST /api/v1/orders/{order_id}/cancel
取消订单. 仅 CREATED/PAID 状态可取消. PAID 状态会触发退款流程 (1-3 工作日到账).

## 商品接口 /api/v1/products

### GET /api/v1/products/search
搜索商品. 查询参数: q (关键词), category, price_min, price_max, sort (price_asc/price_desc/sales_desc), page, size. 默认每页 20, 最大 100.

### GET /api/v1/products/{sku_id}
商品详情. 返回 sku, title, price, stock, images, attributes, reviews_summary.

## 限流策略

- 注册接口: 单 IP 每分钟 5 次
- 登录接口: 单账号每分钟 10 次, 单 IP 每分钟 20 次
- 搜索接口: 单 token 每秒 10 次
- 全局限流: 单实例 5000 QPS, 超过返回 429 Too Many Requests

## 鉴权方式

支持三种:
- JWT Bearer Token (主推, access_token + refresh_token)
- API Key (服务间调用, X-API-Key header)
- OAuth2 (第三方接入, 支持微信/支付宝)

JWT 签名算法: HS256 (默认) / RS256 (高安全场景). 密钥轮换周期 90 天.

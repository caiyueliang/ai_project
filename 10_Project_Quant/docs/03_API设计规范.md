# API 设计规范

## 基本约定
- **Base Path**：`/api`
- **协议**：HTTP(S) + JSON
- **认证**：JWT Bearer Token（`Authorization: Bearer <token>`）
- **分页**：统一使用 `skip` / `limit`（与当前后端一致），并返回 `{ total, items }`

## 响应格式
### 成功响应
- 对于列表：
```json
{ "total": 123, "items": [/*...*/] }
```
- 对于详情：直接返回资源对象。

### 错误响应
- 统一使用 FastAPI 的 HTTP 状态码。
- 错误体建议统一为：
```json
{ "code": "ERROR_CODE", "msg": "错误描述", "detail": { /* 可选 */ } }
```

## 命名与字段规范
- URL：资源名使用复数名词（`/funds`、`/users`）
- Query 参数：使用 `snake_case`（如 `sort_by`、`sort_order`）
- 时间：日期 `YYYY-MM-DD`，时间戳为 ISO 8601

## 当前已实现的关键接口（摘要）

### 认证
- `POST /api/auth/login`：OAuth2 form 登录，返回 token
- `POST /api/auth/register`：注册

### 基金
- `GET /api/funds/`：基金列表（支持筛选/排序/分页）
  - Query：`skip`、`limit`、`type`、`search`、`sort_by`、`sort_order`
  - Response：`{ total, items: [{ code,name,fund_type,nav,nav_date,daily_change_pct }] }`
- `GET /api/funds/{code}`：基金详情（含历史净值）
  - Query：`limit`（默认 180）
- `POST /api/funds/sync?days=N`：手动同步最近 N 天净值并落库

### 用户（管理员）
- `GET /api/users/`：用户列表（需管理员 token）

### 回测（基础）
- `POST /api/backtest/run`


# DevOps 与部署规范

## Docker / Compose 约定
- 目标：本地一键启动前后端、数据库、Redis。
- 端口约定：
  - 前端：`5173`（开发）
  - 后端：`8000`
  - MySQL：`3306`
  - Redis：`6379`

## 环境变量
### 后端
- `DATABASE_URL`
  - SQLite（默认）：`sqlite:///./fund_quant.db`
  - MySQL 示例：`mysql+mysqlconnector://fund_user:fund_pass@db/fund_db`
- `SECRET_KEY`：JWT 密钥（生产必须替换）

### 前端
- `VITE_API_URL`：后端 API 地址（浏览器可访问的 URL）

## 本地开发运行
- 后端：在项目根目录运行（避免相对导入失败）：
  - `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`
- 前端：
  - `npm run dev`

## CI 建议（规划）
- 每次 PR/MR：
  - 后端：`pytest`
  - 前端：`npm run check`
- 主分支：
  - build 镜像并推送
  - 可选：安全扫描（依赖漏洞、镜像漏洞）


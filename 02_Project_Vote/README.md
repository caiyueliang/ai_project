# 在线投票系统（Flask）

本项目提供一个基于 Flask 的在线投票系统，包含用户认证、投票活动管理、投票提交与结果展示、安全防护、Docker 容器部署以及 pytest 单元测试。

## 功能特性
- 用户注册/登录（用户名+密码），管理员与普通用户角色区分
- 密码加密存储（PBKDF2-SHA256 via Werkzeug）
- 投票创建/编辑/删除（管理员权限）
- 设置投票开始/结束时间，支持单选/多选
- 选项管理与描述
- 响应式页面（Bootstrap 模板）
- 即时结果展示（Chart.js）
- 数据存储：SQLite（默认），可通过环境变量切换 MySQL/PostgreSQL
- CSRF 防护（Flask-WTF）
- 投票次数限制：账号+Cookie+简单冷却时间；记录 IP
- 敏感操作日志记录（RotatingFileHandler）
- Dockerfile，Gunicorn 运行；支持环境变量配置
- 单元测试（pytest）

## 环境变量
参考 [.env.sample](.env.sample)：
```
SECRET_KEY=please-change-me
DATABASE_URL=sqlite:///vote.db
MAX_CHOICES_PER_POLL=10
VOTE_COOLDOWN_SECONDS=30
LOG_DIR=logs
```

## 本地运行
1. 安装依赖：
```
pip install -r requirements.txt
```
2. 启动开发服务：
```
python wsgi.py
```
默认运行在 http://127.0.0.1:5000/。

## Docker 运行（Gunicorn）
```
docker build -t vote-app .
docker run -p 8000:8000 --env-file .env vote-app
```
访问 http://127.0.0.1:8000/。

如需与 NGINX 结合部署，可将容器端口映射给 NGINX 反向代理，并启用 `X-Forwarded-For`。示例 NGINX server 配置：
```
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 运行测试
```
pytest -q
```

## 代码结构
- `app/__init__.py` 应用工厂，扩展初始化、蓝图注册、日志
- `app/config.py` 环境变量与应用配置
- `app/models.py` 用户、投票、选项、投票记录模型
- `app/forms.py` WTForms 表单与校验
- `app/routes/` 认证、投票管理与页面路由
- `app/templates/` Jinja 模板（Bootstrap + Chart.js）
- `wsgi.py` 应用入口（Flask/Gunicorn）
- `requirements.txt` 依赖
- `tests/` pytest 用例
- `Dockerfile` 容器部署
- `.env.sample` 环境变量示例

## 安全说明
- 使用 CSRF 防护
- 账号限制结合 Cookie、冷却时间的简单防刷机制，记录 IP
- 重要操作写入日志（logs/app.log）

## 注意
- 若部署在公网上，请使用强随机 `SECRET_KEY`，配置数据库强访问控制与网络隔离，并在 NGINX/反向代理层增加速率限制与 WAF。

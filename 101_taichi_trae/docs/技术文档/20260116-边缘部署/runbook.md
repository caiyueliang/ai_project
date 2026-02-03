## Edge Deploy 本地联调与测试 Runbook

### 一、前置条件

- 已配置 `scripts/dev/backend/.env`，包含：
  - `BACKEND_IMAGE` 指向后端镜像（如：`.../taichu-studio:dev-a3e988e-202601191136`）
  - `MYSQL_SERVICE`、`REDIS_*`、`KUBERNETES_SERVICE_HOST/PORT` 等依赖
- 本地已安装 Docker，并可访问 ai-dx 依赖集群（如通过 kt-connect 建链）。

### 二、启动本地后端

```bash
cd /Users/caiyueliang/project/wzy/taichu-studio
bash scripts/dev/backend/start.sh
bash scripts/dev/backend/health.sh   # 预期输出 “OK 健康检查正常: http://127.0.0.1:8080/health”
```

### 三、在容器内执行 Edge Deploy 用例

```bash
# 进入后端容器安装 pytest 及 json-report 插件（首跑需要）
docker exec taichu_studio bash -lc 'python -m pip install pytest pytest-json-report'

# 在容器内执行 Edge Deploy 单元测试并生成 JSON 报告
docker exec taichu_studio bash -lc '
  cd /home/myapp/myapp/tests && \
  TAICHU_TEST_ADMIN_TOKEN=admin \
  TAICHU_TEST_SENIOR_TOKEN=CYL \
  TAICHU_TEST_RUN_LOCAL_UNIT=1 \
  python -m pytest unit/edge_deploy \
    --env=local \
    --run-local-unit \
    --json-report \
    --json-report-file=../plugin_json_report/.report.json
'
```

### 四、结果解读

- 用例总数：28
- 当前本地环境结果：
  - 通过：26
  - 失败：2（均为 `test_edge_deploy_get_artifact_download_url_success[...]`）
- 失败用例说明：
  - 失败断言：`device = db.session.query(EdgeDevice).filter(EdgeDevice.id == device_id).first(); assert device is not None`
  - 原因：本地 MySQL 中 `edge_device` 未同步写入刚注册的设备记录，导致依据 `device_id` 查询为空；属于“环境数据不完整”问题，而非接口逻辑错误。

### 五、关键命令汇总

- 启动后端：`bash scripts/dev/backend/start.sh`
- 健康检查：`bash scripts/dev/backend/health.sh`
- 容器内执行 Edge Deploy 用例并生成 JSON 报告：
  - 参见第三节命令，报告路径：`/home/myapp/myapp/tests/plugin_json_report/.report.json`


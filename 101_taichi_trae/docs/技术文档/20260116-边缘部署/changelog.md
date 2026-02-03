## 2026-01-23 测试与联调记录

- 本地通过 `scripts/dev/backend/start.sh` 启动后端容器 `taichu_studio`，并用 `health.sh` 验证 `http://127.0.0.1:8080/health` 正常。
- 在容器内执行 `python -m pytest myapp/tests/unit/edge_deploy --env=local --run-local-unit --json-report --json-report-file=plugin_json_report/.report.json`。
- Edge Deploy 相关用例共 28 条，其中 26 条通过，2 条失败：
  - `test_edge_deploy_get_artifact_download_url_success[user_info0]`
  - `test_edge_deploy_get_artifact_download_url_success[user_info1]`
- 失败原因：用例期望通过 `db.session.query(EdgeDevice).filter(EdgeDevice.id == device_id).first()` 查询到刚注册的设备记录，但本地联调环境下数据库未同步写入，返回 `device is None`，与线上环境存在差异。
- 其余用例（设备注册、心跳、命令拉取与租约、Ack 幂等、实例状态上报、设备列表与 artifact 失败路径等）在本地环境全部通过，验证了设计文档中 ED-REG / ED-HB / ED-CMD / ED-ACK / ED-INS / ED-USER-DEV 等主流程。


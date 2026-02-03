# Edge Deploy 测试用例清单（P0）

> 目标：把“设计与预研”阶段的验证计划落到可执行的用例清单，便于阶段 2 开发时直接转成自动化测试（pytest）并补齐联调验收项。

## 约定

- 响应结构：统一 `{"status": <int>, "message": <str>, "result": <any>}`。
- 鉴权：
  - 用户侧：复用现有 session（`g.user`）。
  - 设备侧：`Authorization: Bearer <device_token>`；注册使用一次性 `enrollment_token`。
- 多租户：所有资源必须按 `tenant_id` 隔离；设备 token 必须绑定 `(tenant_id, device_id)`。
- 幂等：
  - `/agent/commands/ack`、`/agent/report_instance_status` 重放不产生副作用，重复请求返回成功。
  - `/agent/commands/pull` 允许返回空列表并保持 cursor 不变。

## 用例清单

| ID | 用例名称 | 关联接口/表 | 前置条件 | 步骤 | 期望结果 | 优先级 | 自动化 |
|---|---|---|---|---|---|---|---|
| ED-REG-001 | Enrollment 注册成功并下发 device_token | `POST /agent/register`；edge_device、edge_device_credential、edge_device_enrollment_token | 有未过期未使用 enrollment_token | 使用 enrollment_token 调 register | 返回 device_id/device_token/poll 参数；token 标记 used；写入 device 与 credential | P0 | 单测 |
| ED-REG-002 | Enrollment token 过期/已使用不可注册 | `POST /agent/register`；edge_device_enrollment_token | enrollment_token 已过期或已 used | 调 register | 返回 status 非 0；不写入 device/credential | P0 | 单测 |
| ED-REG-003 | 同 tenant + device_uid 重复注册为幂等更新 | `POST /agent/register`；edge_device | 设备已存在（同 tenant_id、device_uid） | 重复 register（同 device_uid） | 不新增 device；更新 name/agent_version/runtime_type/capabilities；返回同 device_id | P1 | 单测 |
| ED-HB-001 | 心跳刷新在线状态与 last_seen_at | `POST /agent/heartbeat`；edge_device | 已注册并持有 device_token | 发 heartbeat(status=online) | status=0；edge_device.last_seen_at 更新，status=online | P0 | 单测 |
| ED-HB-002 | token 与 device_id 不匹配拒绝 | `POST /agent/heartbeat` | A 设备 token，B 设备 device_id | 用 A token 上报 B device_id | 返回 NOT_ALLOWED；数据不被更新 | P0 | 单测 |
| ED-CMD-001 | 拉取命令返回 leased 命令并推进 cursor | `POST /agent/commands/pull`；edge_device_command | 设备有 queued 命令（id>cursor） | pull(cursor=旧值) | 返回 commands[]；命令置 leased；返回 cursor=最大 id | P0 | 单测 |
| ED-CMD-002 | 长轮询无命令返回空列表 | `POST /agent/commands/pull` | 无 queued 命令 | pull(long_poll_seconds>0) | 在超时内返回 commands=[]；cursor 不变 | P1 | 单测 |
| ED-CMD-003 | lease 超时命令回滚为 queued 可重试 | `POST /agent/commands/pull`；edge_device_command | 命令已 leased 且 lease_expires_at 已过期且未 ack | 再次 pull | 过期命令回滚 queued 并可再次被取走（attempt_count 可递增） | P0 | 单测 |
| ED-ACK-001 | Ack 成功更新命令状态为 acked | `POST /agent/commands/ack`；edge_device_command | 命令 leased 且属于该 device | ack(success=true) | status=0；命令置 acked；ack_json/ack_at 更新 | P0 | 单测 |
| ED-ACK-002 | Ack 重放幂等 | `POST /agent/commands/ack` | command_id 已 acked | 重复 ack 同 command_id | status=0；不重复副作用；结果保持一致 | P0 | 单测 |
| ED-ACK-003 | Ack 非本设备命令拒绝 | `POST /agent/commands/ack` | command_id 属于其他 device | ack | 返回 NOT_ALLOWED 或 NOT_FOUND；命令不被更新 | P0 | 单测 |
| ED-INS-001 | 上报实例状态更新 edge_deployment_instance | `POST /agent/report_instance_status`；edge_deployment_instance | 实例存在且属于该 tenant/device | report(status=running，带 endpoint/detail) | status=0；实例状态与 last_reported_at 更新；endpoint_json 写入 | P0 | 单测 |
| ED-INS-002 | 上报实例状态重放幂等 | `POST /agent/report_instance_status` | 已上报过同样状态 | 重复 report | status=0；状态不乱跳；无额外副作用 | P0 | 单测 |
| ED-INS-003 | 上报非法 status 枚举被拒绝 | `POST /agent/report_instance_status` | - | report(status=xxx) | 返回 INVALID_INPUT_PARAM | P0 | 单测 |
| ED-ART-001 | 获取制品下载 URL 成功 | `GET /agent/artifacts/{artifact_id}/download_url`；edge_artifact | artifact 存在且属于 tenant | 调 download_url | status=0；返回 url/expires_at | P1 | 单测 |
| ED-USER-DEV-001 | 用户侧分页查询设备列表 | `GET /devices`；edge_device | tenant 下有多设备 | list(page/page_size/keyword/status) | status=0；分页字段正确；仅返回本 tenant 数据 | P0 | 单测 |
| ED-USER-DEP-001 | 创建 deployment 生成 per-device commands | `POST /deployments`；edge_deployment、edge_deployment_instance、edge_device_command | 有 service 与 device_ids | create deployment | status=0；生成实例与 commands；命令 payload 绑定 instance_id | P0 | 集成 |

## 最小验收（联调/E2E）

- 浏览器/脚本完成：创建 service → 创建 deployment → 设备 pull → 设备 ack/report → 用户侧查询 deployment 看到实例状态变化。
- 弱网模拟：重复 ack/report、超时重连、lease 过期回滚后重试，确保不会重复启动或写错实例状态。


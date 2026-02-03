-- Edge Deploy tables (MySQL)
-- Only new tables are introduced; existing serving tables are untouched.

CREATE TABLE IF NOT EXISTS edge_device (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  project_id INT NULL COMMENT '项目 ID（可选，用于项目内设备归属）',
  name VARCHAR(200) NOT NULL COMMENT '设备名称（展示用）',
  device_uid VARCHAR(200) NOT NULL COMMENT '设备唯一标识（如 SN/序列号，同租户内唯一）',
  status VARCHAR(50) NOT NULL DEFAULT 'offline' COMMENT '设备状态：online|offline|unknown',
  last_seen_at DATETIME NULL COMMENT '最后一次心跳时间（服务端接收时间）',
  ip VARCHAR(64) NULL COMMENT '设备上报的 IP（可选）',
  agent_version VARCHAR(50) NULL COMMENT 'Edge Agent 版本号（可选）',
  runtime_type VARCHAR(50) NULL COMMENT '运行环境类型：docker|process（可选）',
  os VARCHAR(50) NULL COMMENT '操作系统（可选，如 linux）',
  arch VARCHAR(50) NULL COMMENT 'CPU 架构（可选，如 amd64/arm64）',
  capabilities_json TEXT NULL COMMENT '设备能力信息 JSON（如是否有 GPU、CPU 型号等）',
  tags_json TEXT NULL COMMENT '设备标签 JSON（如机房/机架等）',
  created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_edge_device_tenant_uid (tenant_id, device_uid),
  KEY idx_edge_device_tenant_status (tenant_id, status),
  KEY idx_edge_device_tenant_project (tenant_id, project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='边缘设备';

CREATE TABLE IF NOT EXISTS edge_device_credential (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  device_id INT NOT NULL COMMENT '设备 ID',
  token_hash VARCHAR(128) NOT NULL COMMENT 'device_token 哈希（只存 hash）',
  token_last4 VARCHAR(8) NULL COMMENT 'device_token 后 4 位（用于排障展示，可选）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  revoked_at DATETIME NULL COMMENT '吊销时间（不为空表示已吊销）',
  PRIMARY KEY (id),
  UNIQUE KEY uk_edge_device_credential_hash (token_hash),
  KEY idx_edge_device_credential_device (device_id),
  CONSTRAINT fk_edge_device_credential_device
    FOREIGN KEY (device_id) REFERENCES edge_device(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备鉴权凭证（device_token）';

CREATE TABLE IF NOT EXISTS edge_device_enrollment_token (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  project_id INT NULL COMMENT '项目 ID（可选）',
  token_hash VARCHAR(128) NOT NULL COMMENT 'enrollment_token 哈希（只存 hash）',
  note VARCHAR(200) NULL COMMENT '备注（可选）',
  created_by VARCHAR(200) NULL COMMENT '创建人（可选）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  expires_at DATETIME NOT NULL COMMENT '过期时间（服务端时间）',
  used_at DATETIME NULL COMMENT '使用时间（核销时间）',
  used_device_id INT NULL COMMENT '核销时绑定的设备 ID（可选）',
  PRIMARY KEY (id),
  UNIQUE KEY uk_edge_enroll_token_hash (token_hash),
  KEY idx_edge_enroll_token_tenant (tenant_id),
  KEY idx_edge_enroll_token_expires (expires_at),
  CONSTRAINT fk_edge_enroll_used_device
    FOREIGN KEY (used_device_id) REFERENCES edge_device(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备注册一次性令牌（enrollment_token）';

CREATE TABLE IF NOT EXISTS edge_artifact (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  type VARCHAR(50) NOT NULL COMMENT '制品类型（如 artifact/config/weights 等）',
  name VARCHAR(200) NOT NULL COMMENT '制品名称',
  version VARCHAR(100) NULL COMMENT '版本（可选）',
  uri VARCHAR(1000) NOT NULL COMMENT '制品存储定位（如对象存储路径或 URL）',
  digest_sha256 VARCHAR(128) NULL COMMENT 'sha256 校验（可选，用于下载校验）',
  size_bytes BIGINT NULL COMMENT '制品大小（字节，可选）',
  extra_json TEXT NULL COMMENT '扩展信息 JSON（可选）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_edge_artifact_tenant_type (tenant_id, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='边缘制品元数据';

CREATE TABLE IF NOT EXISTS edge_service (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  project_id INT NULL COMMENT '项目 ID（可选）',
  name VARCHAR(200) NOT NULL COMMENT '服务模板名称（同租户内唯一）',
  describe VARCHAR(1000) NULL COMMENT '描述（可选）',
  runtime_type VARCHAR(50) NOT NULL DEFAULT 'docker' COMMENT '运行环境类型：docker|process',
  image VARCHAR(500) NULL COMMENT '容器镜像（docker 模式可选）',
  working_dir VARCHAR(200) NULL COMMENT '工作目录（可选）',
  command VARCHAR(2000) NULL COMMENT '启动命令（可选）',
  env_json TEXT NULL COMMENT '环境变量 JSON（可选）',
  ports_json TEXT NULL COMMENT '端口映射 JSON（可选）',
  resources_json TEXT NULL COMMENT '资源需求 JSON（可选，如 CPU/内存/GPU）',
  artifact_id INT NULL COMMENT '关联制品 ID（可选）',
  model_id INT NULL COMMENT '关联模型 ID（可选）',
  model_version_id INT NULL COMMENT '关联模型版本 ID（可选）',
  created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_edge_service_tenant_name (tenant_id, name),
  KEY idx_edge_service_tenant_project (tenant_id, project_id),
  KEY idx_edge_service_artifact (artifact_id),
  KEY idx_edge_service_model (model_id, model_version_id),
  CONSTRAINT fk_edge_service_artifact
    FOREIGN KEY (artifact_id) REFERENCES edge_artifact(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='边缘服务模板';

CREATE TABLE IF NOT EXISTS edge_deployment (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  service_id INT NOT NULL COMMENT '服务模板 ID',
  status VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '部署状态（如 pending/running/failed 等）',
  strategy VARCHAR(50) NOT NULL DEFAULT 'all_at_once' COMMENT '发布策略（如 all_at_once/batch/canary，P0 先用 all_at_once）',
  desired_version VARCHAR(200) NULL COMMENT '期望版本（可选，如镜像 tag 或制品版本）',
  summary_json TEXT NULL COMMENT '汇总信息 JSON（可选，如运行/失败数量等）',
  created_by VARCHAR(200) NULL COMMENT '创建人（可选）',
  created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  changed_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_edge_deploy_tenant_status (tenant_id, status),
  KEY idx_edge_deploy_service (service_id),
  CONSTRAINT fk_edge_deploy_service
    FOREIGN KEY (service_id) REFERENCES edge_service(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='边缘部署记录';

CREATE TABLE IF NOT EXISTS edge_deployment_instance (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主键',
  deployment_id INT NOT NULL COMMENT '部署 ID',
  device_id INT NOT NULL COMMENT '设备 ID',
  status VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '实例状态：pending|downloading|starting|running|stopped|failed|unknown',
  current_version VARCHAR(200) NULL COMMENT '当前运行版本（可选）',
  endpoint_json TEXT NULL COMMENT '服务访问端点 JSON（可选）',
  last_error TEXT NULL COMMENT '最近错误信息（可选）',
  last_reported_at DATETIME NULL COMMENT '最后一次状态上报时间（服务端接收时间）',
  created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_edge_instance_deploy_device (deployment_id, device_id),
  KEY idx_edge_instance_device_status (device_id, status),
  CONSTRAINT fk_edge_instance_deploy
    FOREIGN KEY (deployment_id) REFERENCES edge_deployment(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_edge_instance_device
    FOREIGN KEY (device_id) REFERENCES edge_device(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='边缘部署实例（按设备）';

CREATE TABLE IF NOT EXISTS edge_device_command (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键（递增，亦可作为 cursor）',
  tenant_id VARCHAR(100) NOT NULL COMMENT '租户 ID（隔离维度）',
  device_id INT NOT NULL COMMENT '目标设备 ID',
  instance_id INT NULL COMMENT '关联部署实例 ID（可选）',
  type VARCHAR(50) NOT NULL COMMENT '命令类型（如 download_artifact/start/stop/restart 等）',
  payload_json TEXT NULL COMMENT '命令参数 JSON（可选）',
  payload_hash VARCHAR(128) NULL COMMENT 'payload 哈希（用于幂等键，可选）',
  status VARCHAR(50) NOT NULL DEFAULT 'queued' COMMENT '命令状态：queued|leased|acked|failed|cancelled',
  priority INT NOT NULL DEFAULT 0 COMMENT '优先级（数值越大越优先）',
  next_visible_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下次可被拉取的时间（用于延迟与退避重试）',
  lease_owner_device_id INT NULL COMMENT '租约持有者设备 ID（通常等于 device_id）',
  leased_at DATETIME NULL COMMENT '租约开始时间',
  lease_expires_at DATETIME NULL COMMENT '租约过期时间（超时未 ack 回滚 queued）',
  attempt_count INT NOT NULL DEFAULT 0 COMMENT '尝试次数（拉取并 lease 记一次或按实现计数）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  ack_at DATETIME NULL COMMENT '回执时间',
  ack_json TEXT NULL COMMENT '回执详情 JSON（如 success、duration、错误摘要等）',
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_edge_cmd_device_status_visible_time (device_id, status, next_visible_at, created_at),
  KEY idx_edge_cmd_status_lease_exp (status, lease_expires_at),
  UNIQUE KEY uk_edge_cmd_device_type_payload_instance (device_id, type, payload_hash, instance_id),
  KEY idx_edge_cmd_instance (instance_id),
  CONSTRAINT fk_edge_cmd_device
    FOREIGN KEY (device_id) REFERENCES edge_device(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_edge_cmd_instance
    FOREIGN KEY (instance_id) REFERENCES edge_deployment_instance(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备命令队列（租约/重试/回执）';

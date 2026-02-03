# 台词基本功智能训练系统 - 技术设计文档

## 项目概述
基于FastAPI的舞台艺术言语基本功智能训练系统，提供学生训练记录、教师评价和AI语音分析功能。

## 技术栈
- **后端**: Python FastAPI, SQLAlchemy, MySQL
- **前端**: React + TypeScript
- **AI服务**: 阿里云/科大讯飞ASR API
- **存储**: 对象存储(MinIO/阿里云OSS)
- **部署**: Docker + Nginx

## 数据库设计 (MySQL)

### 核心表结构

#### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL COMMENT '学校系统用户ID',
    name VARCHAR(100) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    class_id VARCHAR(50) COMMENT '班级ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_id (user_id)
);
```

#### 2. 训练会话表 (training_sessions)
```sql
CREATE TABLE training_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    content_text TEXT COMMENT '训练文本内容',
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration INT COMMENT '训练时长(秒)',
    audio_url VARCHAR(500) COMMENT '音频文件地址',
    video_url VARCHAR(500) COMMENT '视频文件地址',
    asr_text TEXT COMMENT 'ASR转写文本',
    env_check_result VARCHAR(50) COMMENT '环境检测结果',
    status ENUM('recording', 'completed', 'processing', 'evaluated') DEFAULT 'recording',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);
```

#### 3. 教师评价表 (teacher_evaluations)
```sql
CREATE TABLE teacher_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    teacher_id INT NOT NULL,
    timestamp_seconds INT COMMENT '评价时间点(秒)',
    comment TEXT COMMENT '评语内容',
    score INT COMMENT '评分(0-100)',
    dimension ENUM('pronunciation', 'emotion', 'rhythm', 'articulation') COMMENT '评价维度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES training_sessions(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

#### 4. 训练任务表 (training_tasks)
```sql
CREATE TABLE training_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_text TEXT NOT NULL,
    deadline DATETIME,
    target_class VARCHAR(50) COMMENT '目标班级',
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

## 项目结构
```
taichi-training-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI主应用
│   │   ├── models.py            # SQLAlchemy模型
│   │   ├── schemas.py           # Pydantic模型
│   │   ├── database.py          # 数据库配置
│   │   ├── api/
│   │   │   ├── endpoints.py     # API路由
│   │   │   ├── auth.py          # 认证路由
│   │   │   └── ai_services.py   # AI服务集成
│   │   └── services/
│   │       ├── training_service.py
│   │       ├── evaluation_service.py
│   │       └── storage_service.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API设计

### 1. 训练相关API
- `POST /api/training/sessions` - 创建训练会话
- `PUT /api/training/sessions/{session_id}` - 更新训练会话(结束训练)
- `GET /api/training/sessions` - 获取训练会话列表
- `GET /api/training/sessions/{session_id}` - 获取会话详情

### 2. 评价相关API  
- `POST /api/evaluations` - 添加教师评价
- `GET /api/evaluations/session/{session_id}` - 获取会话评价
- `GET /api/evaluations/statistics` - 获取统计报告

### 3. 任务管理API
- `POST /api/tasks` - 创建训练任务
- `GET /api/tasks` - 获取任务列表
- `PUT /api/tasks/{task_id}` - 更新任务状态

## 下一步开发计划
1. 设置MySQL数据库和表结构
2. 创建FastAPI后端基础框架
3. 实现核心API端点
4. 集成ASR语音识别服务
5. 开发React前端界面
6. 部署测试环境
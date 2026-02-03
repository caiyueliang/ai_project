-- 创建数据库用户（如果不存在）
CREATE USER IF NOT EXISTS 'taichi_user'@'%' IDENTIFIED BY 'taichi_password';
GRANT ALL PRIVILEGES ON taichi_training.* TO 'taichi_user'@'%';
FLUSH PRIVILEGES;

-- 使用数据库
USE taichi_training;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL COMMENT '学校系统用户ID',
    name VARCHAR(100) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    class_id VARCHAR(50) COMMENT '班级ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_id (user_id)
);

-- 创建训练会话表
CREATE TABLE IF NOT EXISTS training_sessions (
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

-- 创建教师评价表
CREATE TABLE IF NOT EXISTS teacher_evaluations (
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

-- 创建训练任务表
CREATE TABLE IF NOT EXISTS training_tasks (
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

-- 插入示例数据
INSERT INTO users (user_id, name, role, class_id) VALUES
('S001', '张三', 'student', 'class1'),
('S002', '李四', 'student', 'class1'),
('T001', '王老师', 'teacher', 'class1'),
('A001', '管理员', 'admin', NULL);

INSERT INTO training_sessions (student_id, content_text, start_time, end_time, duration, status) VALUES
(1, '白日依山尽，黄河入海流。欲穷千里目，更上一层楼。', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 300 SECOND, 300, 'completed'),
(2, '床前明月光，疑是地上霜。举头望明月，低头思故乡。', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 240 SECOND, 240, 'completed');

INSERT INTO teacher_evaluations (session_id, teacher_id, timestamp_seconds, comment, score, dimension) VALUES
(1, 3, 60, '发音清晰，情感饱满', 85, 'pronunciation'),
(1, 3, 120, '节奏感很好', 90, 'rhythm'),
(2, 3, 30, '情感表达需要加强', 75, 'emotion');

INSERT INTO training_tasks (teacher_id, title, content_text, deadline, target_class) VALUES
(3, '古诗朗诵训练', '请朗诵《静夜思》并注意情感表达', NOW() + INTERVAL 7 DAY, 'class1');
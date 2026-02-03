from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class TrainingStatus(str, enum.Enum):
    RECORDING = "recording"
    COMPLETED = "completed"
    PROCESSING = "processing"
    EVALUATED = "evaluated"

class EvaluationDimension(str, enum.Enum):
    PRONUNCIATION = "pronunciation"
    EMOTION = "emotion"
    RHYTHM = "rhythm"
    ARTICULATION = "articulation"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, comment="学校系统用户ID")
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    class_id = Column(String(50), comment="班级ID")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_text = Column(Text, comment="训练文本内容")
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer, comment="训练时长(秒)")
    audio_url = Column(String(500), comment="音频文件地址")
    video_url = Column(String(500), comment="视频文件地址")
    asr_text = Column(Text, comment="ASR转写文本")
    env_check_result = Column(String(50), comment="环境检测结果")
    status = Column(Enum(TrainingStatus), default=TrainingStatus.RECORDING)
    created_at = Column(DateTime, default=func.now())

class TeacherEvaluation(Base):
    __tablename__ = "teacher_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp_seconds = Column(Integer, comment="评价时间点(秒)")
    comment = Column(Text, comment="评语内容")
    score = Column(Integer, comment="评分(0-100)")
    dimension = Column(Enum(EvaluationDimension), comment="评价维度")
    created_at = Column(DateTime, default=func.now())

class TrainingTask(Base):
    __tablename__ = "training_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content_text = Column(Text, nullable=False)
    deadline = Column(DateTime)
    target_class = Column(String(50), comment="目标班级")
    status = Column(Enum('active', 'completed', 'cancelled'), default='active')
    created_at = Column(DateTime, default=func.now())
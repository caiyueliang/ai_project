from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 枚举类
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class TrainingStatus(str, Enum):
    RECORDING = "recording"
    COMPLETED = "completed"
    PROCESSING = "processing"
    EVALUATED = "evaluated"

class EvaluationDimension(str, Enum):
    PRONUNCIATION = "pronunciation"
    EMOTION = "emotion"
    RHYTHM = "rhythm"
    ARTICULATION = "articulation"

# 基础模型
class BaseResponse(BaseModel):
    id: int
    created_at: datetime

# 用户相关
class UserCreate(BaseModel):
    user_id: str = Field(..., description="学校系统用户ID")
    name: str = Field(..., max_length=100)
    role: UserRole
    class_id: Optional[str] = Field(None, max_length=50)

class UserResponse(BaseResponse):
    user_id: str
    name: str
    role: UserRole
    class_id: Optional[str]

# 训练会话相关
class TrainingSessionCreate(BaseModel):
    content_text: str = Field(..., description="训练文本内容")
    start_time: datetime = Field(..., description="训练开始时间")

class TrainingSessionResponse(BaseResponse):
    student_id: int
    content_text: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    audio_url: Optional[str]
    video_url: Optional[str]
    asr_text: Optional[str]
    env_check_result: Optional[str]
    status: TrainingStatus
    student: UserResponse

# 教师评价相关
class TeacherEvaluationCreate(BaseModel):
    session_id: int = Field(..., description="训练会话ID")
    timestamp_seconds: int = Field(..., description="评价时间点(秒)")
    comment: str = Field(..., description="评语内容")
    score: int = Field(..., ge=0, le=100, description="评分(0-100)")
    dimension: EvaluationDimension = Field(..., description="评价维度")

class TeacherEvaluationResponse(BaseResponse):
    session_id: int
    teacher_id: int
    timestamp_seconds: int
    comment: str
    score: int
    dimension: EvaluationDimension
    teacher: UserResponse

# 训练任务相关
class TrainingTaskCreate(BaseModel):
    title: str = Field(..., max_length=200, description="任务标题")
    content_text: str = Field(..., description="训练文本内容")
    deadline: Optional[datetime] = Field(None, description="截止时间")
    target_class: Optional[str] = Field(None, max_length=50, description="目标班级")

class TrainingTaskResponse(BaseResponse):
    teacher_id: int
    title: str
    content_text: str
    deadline: Optional[datetime]
    target_class: Optional[str]
    status: str
    teacher: UserResponse

# 认证相关
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# 统计相关
class EvaluationStatistics(BaseModel):
    session_id: int
    avg_score: float
    total_evaluations: int
    dimension_scores: dict

class StudentProgress(BaseModel):
    student_id: int
    total_sessions: int
    avg_score: float
    improvement_rate: float
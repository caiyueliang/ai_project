from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import User, UserRole, TrainingStatus
from schemas import (
    TrainingSessionCreate, TrainingSessionResponse,
    TeacherEvaluationCreate, TeacherEvaluationResponse,
    TrainingTaskCreate, TrainingTaskResponse
)
from services.training_service import TrainingService
from services.evaluation_service import EvaluationService
from services.storage_service import StorageService
from .auth import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

# 训练会话路由
@router.post("/training/sessions", response_model=TrainingSessionResponse)
def create_training_session(
    session_data: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="只有学生可以创建训练会话")
    
    return TrainingService.create_session(db, current_user.id, session_data)

@router.post("/training/sessions/{session_id}/upload-audio")
async def upload_session_audio(
    session_id: int,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证会话所有权
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session or session.student_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    # 读取文件内容
    file_data = await audio_file.read()
    
    # 上传到对象存储
    storage_service = StorageService()
    audio_url = storage_service.upload_audio(
        file_data, audio_file.filename, current_user.user_id
    )
    
    if audio_url:
        session.audio_url = audio_url
        session.status = TrainingStatus.COMPLETED
        session.end_time = datetime.now()
        session.duration = int((session.end_time - session.start_time).total_seconds())
        db.commit()
        db.refresh(session)
    
    return {"audio_url": audio_url}

@router.get("/training/sessions", response_model=List[TrainingSessionResponse])
def get_training_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.STUDENT:
        return TrainingService.get_student_sessions(db, current_user.id, skip, limit)
    elif current_user.role == UserRole.TEACHER:
        return TrainingService.get_teacher_sessions(db, current_user.id, skip, limit)
    else:
        return TrainingService.get_all_sessions(db, skip, limit)

@router.get("/training/sessions/{session_id}", response_model=TrainingSessionResponse)
def get_training_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = TrainingService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 权限检查
    if (current_user.role == UserRole.STUDENT and session.student_id != current_user.id) or \
       (current_user.role == UserRole.TEACHER and session.student.class_id != current_user.class_id):
        raise HTTPException(status_code=403, detail="无权访问此会话")
    
    return session

# 教师评价路由
@router.post("/evaluations", response_model=TeacherEvaluationResponse)
def create_evaluation(
    evaluation_data: TeacherEvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="只有教师可以创建评价")
    
    return EvaluationService.create_evaluation(db, current_user.id, evaluation_data)

@router.get("/evaluations/session/{session_id}", response_model=List[TeacherEvaluationResponse])
def get_session_evaluations(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EvaluationService.get_session_evaluations(db, session_id)

@router.get("/evaluations/statistics/{session_id}")
def get_evaluation_statistics(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EvaluationService.get_evaluation_statistics(db, session_id)

# 训练任务路由
@router.post("/tasks", response_model=TrainingTaskResponse)
def create_task(
    task_data: TrainingTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="只有教师可以创建任务")
    
    return TrainingService.create_task(db, current_user.id, task_data)

@router.get("/tasks", response_model=List[TrainingTaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return TrainingService.get_tasks(db, current_user, skip, limit)

# 学生进度路由
@router.get("/progress/student/{student_id}")
def get_student_progress(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 权限检查：教师只能查看自己班级的学生进度
    if current_user.role == UserRole.TEACHER:
        student = db.query(User).filter(User.id == student_id).first()
        if not student or student.class_id != current_user.class_id:
            raise HTTPException(status_code=403, detail="无权查看该学生进度")
    elif current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="只能查看自己的进度")
    
    return EvaluationService.get_student_progress(db, student_id)
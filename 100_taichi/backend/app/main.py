from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from typing import List

from database import get_db, settings
from models import User, UserRole
from schemas import (
    UserCreate, UserResponse, Token, TrainingSessionCreate, TrainingSessionResponse,
    TeacherEvaluationCreate, TeacherEvaluationResponse, TrainingTaskCreate, TrainingTaskResponse
)
from services.training_service import TrainingService
from services.evaluation_service import EvaluationService
from services.storage_service import StorageService

app = FastAPI(title="台词基本功智能训练系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 依赖函数：获取当前用户
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# 认证路由
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 这里简化处理，实际应该验证密码
    user = db.query(User).filter(User.user_id == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# 训练会话路由
@app.post("/api/training/sessions", response_model=TrainingSessionResponse)
def create_training_session(
    session_data: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="只有学生可以创建训练会话")
    
    return TrainingService.create_session(db, current_user.id, session_data)

@app.get("/api/training/sessions", response_model=List[TrainingSessionResponse])
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

@app.get("/api/training/sessions/{session_id}", response_model=TrainingSessionResponse)
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
@app.post("/api/evaluations", response_model=TeacherEvaluationResponse)
def create_evaluation(
    evaluation_data: TeacherEvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="只有教师可以创建评价")
    
    return EvaluationService.create_evaluation(db, current_user.id, evaluation_data)

@app.get("/api/evaluations/session/{session_id}", response_model=List[TeacherEvaluationResponse])
def get_session_evaluations(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EvaluationService.get_session_evaluations(db, session_id)

# 训练任务路由
@app.post("/api/tasks", response_model=TrainingTaskResponse)
def create_task(
    task_data: TrainingTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="只有教师可以创建任务")
    
    return TrainingService.create_task(db, current_user.id, task_data)

@app.get("/api/tasks", response_model=List[TrainingTaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return TrainingService.get_tasks(db, current_user, skip, limit)

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
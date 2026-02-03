from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models import TrainingSession, TrainingTask, User, TrainingStatus
from ..schemas import TrainingSessionCreate, TrainingSessionResponse, TrainingTaskCreate, TrainingTaskResponse

class TrainingService:
    
    @staticmethod
    def create_session(db: Session, student_id: int, session_data: TrainingSessionCreate) -> TrainingSessionResponse:
        session = TrainingSession(
            student_id=student_id,
            content_text=session_data.content_text,
            start_time=session_data.start_time,
            status=TrainingStatus.RECORDING
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return TrainingService._session_to_response(session)
    
    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[TrainingSessionResponse]:
        session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if session:
            return TrainingService._session_to_response(session)
        return None
    
    @staticmethod
    def get_student_sessions(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[TrainingSessionResponse]:
        sessions = db.query(TrainingSession).filter(
            TrainingSession.student_id == student_id
        ).offset(skip).limit(limit).all()
        return [TrainingService._session_to_response(session) for session in sessions]
    
    @staticmethod
    def get_teacher_sessions(db: Session, teacher_id: int, skip: int = 0, limit: int = 100) -> List[TrainingSessionResponse]:
        # 获取教师所在班级的学生会话
        teacher = db.query(User).filter(User.id == teacher_id).first()
        if not teacher or not teacher.class_id:
            return []
        
        sessions = db.query(TrainingSession).join(User).filter(
            User.class_id == teacher.class_id
        ).offset(skip).limit(limit).all()
        return [TrainingService._session_to_response(session) for session in sessions]
    
    @staticmethod
    def get_all_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[TrainingSessionResponse]:
        sessions = db.query(TrainingSession).offset(skip).limit(limit).all()
        return [TrainingService._session_to_response(session) for session in sessions]
    
    @staticmethod
    def update_session_status(db: Session, session_id: int, status: TrainingStatus, **kwargs):
        session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if session:
            session.status = status
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            db.commit()
            db.refresh(session)
    
    @staticmethod
    def create_task(db: Session, teacher_id: int, task_data: TrainingTaskCreate) -> TrainingTaskResponse:
        task = TrainingTask(
            teacher_id=teacher_id,
            title=task_data.title,
            content_text=task_data.content_text,
            deadline=task_data.deadline,
            target_class=task_data.target_class
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return TrainingService._task_to_response(task)
    
    @staticmethod
    def get_tasks(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[TrainingTaskResponse]:
        if current_user.role == "teacher":
            tasks = db.query(TrainingTask).filter(
                TrainingTask.teacher_id == current_user.id
            ).offset(skip).limit(limit).all()
        elif current_user.role == "student":
            tasks = db.query(TrainingTask).filter(
                (TrainingTask.target_class == current_user.class_id) | (TrainingTask.target_class == None)
            ).offset(skip).limit(limit).all()
        else:
            tasks = db.query(TrainingTask).offset(skip).limit(limit).all()
        
        return [TrainingService._task_to_response(task) for task in tasks]
    
    @staticmethod
    def _session_to_response(session: TrainingSession) -> TrainingSessionResponse:
        return TrainingSessionResponse(
            id=session.id,
            student_id=session.student_id,
            content_text=session.content_text,
            start_time=session.start_time,
            end_time=session.end_time,
            duration=session.duration,
            audio_url=session.audio_url,
            video_url=session.video_url,
            asr_text=session.asr_text,
            env_check_result=session.env_check_result,
            status=session.status,
            created_at=session.created_at,
            student=UserResponse(
                id=session.student.id,
                user_id=session.student.user_id,
                name=session.student.name,
                role=session.student.role,
                class_id=session.student.class_id,
                created_at=session.student.created_at
            )
        )
    
    @staticmethod
    def _task_to_response(task: TrainingTask) -> TrainingTaskResponse:
        return TrainingTaskResponse(
            id=task.id,
            teacher_id=task.teacher_id,
            title=task.title,
            content_text=task.content_text,
            deadline=task.deadline,
            target_class=task.target_class,
            status=task.status,
            created_at=task.created_at,
            teacher=UserResponse(
                id=task.teacher.id,
                user_id=task.teacher.user_id,
                name=task.teacher.name,
                role=task.teacher.role,
                class_id=task.teacher.class_id,
                created_at=task.teacher.created_at
            )
        )
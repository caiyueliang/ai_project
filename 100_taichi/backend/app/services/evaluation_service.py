from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from ..models import TeacherEvaluation, TrainingSession, User
from ..schemas import TeacherEvaluationCreate, TeacherEvaluationResponse, EvaluationStatistics

class EvaluationService:
    
    @staticmethod
    def create_evaluation(db: Session, teacher_id: int, evaluation_data: TeacherEvaluationCreate) -> TeacherEvaluationResponse:
        evaluation = TeacherEvaluation(
            session_id=evaluation_data.session_id,
            teacher_id=teacher_id,
            timestamp_seconds=evaluation_data.timestamp_seconds,
            comment=evaluation_data.comment,
            score=evaluation_data.score,
            dimension=evaluation_data.dimension
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 更新会话状态为已评价
        session = db.query(TrainingSession).filter(TrainingSession.id == evaluation_data.session_id).first()
        if session:
            session.status = "evaluated"
            db.commit()
        
        return EvaluationService._evaluation_to_response(evaluation)
    
    @staticmethod
    def get_session_evaluations(db: Session, session_id: int) -> List[TeacherEvaluationResponse]:
        evaluations = db.query(TeacherEvaluation).filter(
            TeacherEvaluation.session_id == session_id
        ).all()
        return [EvaluationService._evaluation_to_response(eval) for eval in evaluations]
    
    @staticmethod
    def get_evaluation_statistics(db: Session, session_id: int) -> EvaluationStatistics:
        # 计算平均分和维度分数
        stats = db.query(
            func.avg(TeacherEvaluation.score).label('avg_score'),
            func.count(TeacherEvaluation.id).label('total_evaluations'),
            TeacherEvaluation.dimension
        ).filter(
            TeacherEvaluation.session_id == session_id
        ).group_by(TeacherEvaluation.dimension).all()
        
        dimension_scores = {}
        total_score = 0
        total_count = 0
        
        for stat in stats:
            dimension_scores[stat.dimension] = float(stat.avg_score) if stat.avg_score else 0
            total_score += stat.avg_score * stat.total_evaluations
            total_count += stat.total_evaluations
        
        avg_score = total_score / total_count if total_count > 0 else 0
        
        return EvaluationStatistics(
            session_id=session_id,
            avg_score=avg_score,
            total_evaluations=total_count,
            dimension_scores=dimension_scores
        )
    
    @staticmethod
    def get_student_progress(db: Session, student_id: int) -> dict:
        # 获取学生所有会话的统计信息
        sessions = db.query(TrainingSession).filter(
            TrainingSession.student_id == student_id,
            TrainingSession.status == "evaluated"
        ).all()
        
        progress_data = []
        for session in sessions:
            stats = EvaluationService.get_evaluation_statistics(db, session.id)
            progress_data.append({
                "session_id": session.id,
                "date": session.created_at,
                "avg_score": stats.avg_score,
                "total_evaluations": stats.total_evaluations
            })
        
        return {
            "student_id": student_id,
            "total_sessions": len(sessions),
            "progress_data": progress_data
        }
    
    @staticmethod
    def _evaluation_to_response(evaluation: TeacherEvaluation) -> TeacherEvaluationResponse:
        return TeacherEvaluationResponse(
            id=evaluation.id,
            session_id=evaluation.session_id,
            teacher_id=evaluation.teacher_id,
            timestamp_seconds=evaluation.timestamp_seconds,
            comment=evaluation.comment,
            score=evaluation.score,
            dimension=evaluation.dimension,
            created_at=evaluation.created_at,
            teacher=UserResponse(
                id=evaluation.teacher.id,
                user_id=evaluation.teacher.user_id,
                name=evaluation.teacher.name,
                role=evaluation.teacher.role,
                class_id=evaluation.teacher.class_id,
                created_at=evaluation.teacher.created_at
            )
        )
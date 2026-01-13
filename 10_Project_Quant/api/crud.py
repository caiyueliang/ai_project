from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_funds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Fund).offset(skip).limit(limit).all()

def create_backtest(db: Session, backtest: schemas.BacktestCreate, user_id: int, task_id: str):
    db_backtest = models.Backtest(
        user_id=user_id,
        task_id=task_id,
        strategy_params=backtest.strategy_params,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        fund_codes=backtest.fund_codes,
        status=models.BacktestStatus.pending
    )
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)
    return db_backtest

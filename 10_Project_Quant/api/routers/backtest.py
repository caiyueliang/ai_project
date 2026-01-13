from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database
import uuid

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

@router.post("/run", response_model=schemas.BacktestResponse)
def run_backtest(backtest: schemas.BacktestCreate, db: Session = Depends(database.get_db)):
    # Mock user_id for now or get from auth
    # In real app, we would get user from token dependency
    # For now, let's assume user_id=1 (admin) if user exists, else need to handle it
    # But since we haven't implemented full auth dependency injection here yet
    # We will assume a default user for testing or raise error if not found
    user_id = 1 
    task_id = str(uuid.uuid4())
    return crud.create_backtest(db=db, backtest=backtest, user_id=user_id, task_id=task_id)

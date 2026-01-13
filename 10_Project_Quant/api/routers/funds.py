from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/api/funds", tags=["funds"])

@router.get("/", response_model=List[schemas.FundResponse])
def read_funds(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    funds = crud.get_funds(db, skip=skip, limit=limit)
    return funds
